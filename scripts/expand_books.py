"""
从 BookDouban250.csv 生成完整的 books.json：
- 全部 247 本书
- 自动下载封面
- 自动分类 + 生成推荐语
用法: python scripts/expand_books.py
"""
import csv, json, os, re, time, urllib.request, ssl

CSV_PATH = "src/data/BookDouban250.csv"
BOOKS_PATH = "src/data/books.json"
COVERS_DIR = "public/covers"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": "https://book.douban.com/",
}

# 分类关键词映射
CATEGORY_RULES = [
    (["经济", "商业", "创业", "投资", "管理", "营销", "金融", "理财", "资本"], "商业"),
    (["心理", "思维", "脑", "认知", "沟通", "情绪", "行为"], "心理学"),
    (["哲学", "存在", "意义", "智慧", "理性", "伦理", "道德", "逻辑"], "哲学"),
    (["历史", "战争", "革命", "帝国", "文明", "古代", "近代", "二战", "文革", "明朝", "清朝", "中国史", "世界史"], "历史"),
    (["科幻", "宇宙", "外星", "时间旅行", "人工智能", "太空", "未来", "机器人"], "科幻"),
    (["推理", "悬疑", "侦探", "谋杀", "凶案", "犯罪", "谜"], "推理"),
    (["社会", "政治", "文化", "人类学", "社会性", "群体", "国家", "制度", "民主", "权力"], "社科"),
    (["科学", "物理", "数学", "生物", "编程", "计算机", "技术", "量子", "基因", "进化"], "科技"),
    (["传记", "回忆录", "自传", "生平"], "传记"),
    (["童话", "儿童", "少年", "冒险", "奇幻", "魔法", "神话"], "童话"),
    (["成长", "自控", "习惯", "效率", "成功", "学习", "阅读"], "成长"),
]

def classify(title, desc):
    """根据书名和简介自动分类"""
    text = title + desc
    for keywords, category in CATEGORY_RULES:
        for kw in keywords:
            if kw in text:
                return category
    return "小说"  # 默认

def reason_from_desc(desc, rating):
    """根据简介生成推荐语"""
    if rating:
        return f"{desc} 豆瓣评分{rating}。"
    return desc

def fetch_page(url):
    req = urllib.request.Request(url, headers=HEADERS)
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except:
        return None

def get_cover_url(subject_id):
    url = f"https://book.douban.com/subject/{subject_id}/"
    html = fetch_page(url)
    if not html:
        return None
    for pattern in [
        r'"pic"\s*:\s*"([^"]+)"',
        r'property="og:image"\s+content="([^"]+)"',
        r'<img[^>]*src="([^"]*view/subject/[^"]*public[^"]+)"',
    ]:
        m = re.search(pattern, html)
        if m:
            cover = m.group(1).replace("/m/", "/l/").replace("/s/", "/l/")
            return cover.replace("&amp;", "&")
    return None

def download_cover(cover_url, filepath):
    if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
        return True
    req = urllib.request.Request(cover_url, headers=HEADERS)
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
            if resp.status == 200:
                data = resp.read()
                if len(data) > 1000:
                    with open(filepath, "wb") as f:
                        f.write(data)
                    return True
    except:
        pass
    return False

def main():
    os.makedirs(COVERS_DIR, exist_ok=True)

    # 读取 CSV
    csv_books = []
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            title = row.get("书名", "").strip()
            if not title:
                continue
            csv_books.append({
                "title": title,
                "author": re.sub(r"\s+", " ", row.get("作者", "")).strip(),
                "description": row.get("简介", "").strip(),
                "douban_url": row.get("豆瓣链接", "").strip(),
                "rating": row.get("评分", "").strip(),
                "publisher": row.get("出版社", "").strip(),
            })

    print(f"CSV 共 {len(csv_books)} 本书\n")

    # 加载已有 books.json（保留已有的 reason 和 category）
    existing = {}
    if os.path.exists(BOOKS_PATH):
        with open(BOOKS_PATH, "r", encoding="utf-8") as f:
            old_books = json.load(f)
            for b in old_books:
                existing[b["title"]] = b

    new_books = []
    cover_ok = 0
    next_id = 1

    for i, csv_book in enumerate(csv_books):
        title = csv_book["title"]
        book_id = str(next_id)

        # 如果已有这本书，保留其 reason 和 category
        old = existing.get(title)
        category = old["category"] if old else classify(title, csv_book["description"])
        reason = old["reason"] if old and "reason" in old else reason_from_desc(csv_book["description"], csv_book["rating"])

        # 提取 subject ID
        match = re.search(r"/subject/(\d+)/", csv_book["douban_url"])
        subject_id = match.group(1) if match else None

        # 封面优先用已有的，否则从豆瓣下载
        cover_path = old["cover"] if old and old.get("cover", "").startswith("/book-daily/covers/") else ""

        if not cover_path and subject_id:
            print(f"[{i+1}/{len(csv_books)}] {title} ...", end=" ", flush=True)
            cover_url = get_cover_url(subject_id)
            if cover_url:
                filepath = os.path.join(COVERS_DIR, f"{book_id}.jpg")
                if download_cover(cover_url, filepath):
                    cover_path = f"/book-daily/covers/{book_id}.jpg"
                    print("✅")
                    cover_ok += 1
                else:
                    print("⚠️ 下载失败")
            else:
                print("⚠️ 无封面")
            time.sleep(2)
        else:
            print(f"[{i+1}/{len(csv_books)}] {title} (使用已有数据)")

        book = {
            "id": book_id,
            "title": title,
            "author": csv_book["author"],
            "cover": cover_path,
            "description": csv_book["description"],
            "reason": reason,
            "category": category,
        }
        if csv_book["douban_url"]:
            book["doubanUrl"] = csv_book["douban_url"]

        new_books.append(book)
        next_id += 1

    with open(BOOKS_PATH, "w", encoding="utf-8") as f:
        json.dump(new_books, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 共 {len(new_books)} 本书, 封面下载成功 {cover_ok}")

if __name__ == "__main__":
    main()
