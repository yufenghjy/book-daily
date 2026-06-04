"""
根据 BookDouban250.csv 修正 books.json 的元数据和封面
用法: python scripts/fix_from_csv.py
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


def load_csv():
    """解析 CSV 文件，返回 {书名: info} 字典"""
    book_map = {}
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row.get("书名", "").strip()
            if title:
                book_map[title] = {
                    "author": row.get("作者", "").strip(),
                    "description": row.get("简介", "").strip(),
                    "douban_url": row.get("豆瓣链接", "").strip(),
                    "rating": row.get("评分", "").strip(),
                    "publisher": row.get("出版社", "").strip(),
                }
    return book_map


def fetch_page(url):
    """获取网页内容"""
    req = urllib.request.Request(url, headers=HEADERS)
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        return None


def get_cover_url(subject_id):
    """从豆瓣书籍页提取封面图 URL"""
    url = f"https://book.douban.com/subject/{subject_id}/"
    html = fetch_page(url)
    if not html:
        return None

    # 多种方式提取封面
    for pattern in [
        r'"pic"\s*:\s*"([^"]+)"',
        r'property="og:image"\s+content="([^"]+)"',
        r'<img[^>]*src="([^"]*view/subject/[^"]*public[^"]+)"',
        r'cover-image.*?src="([^"]+)"',
    ]:
        m = re.search(pattern, html)
        if m:
            cover = m.group(1)
            # 统一用大图
            cover = cover.replace("/m/", "/l/").replace("/s/", "/l/")
            cover = cover.replace("&amp;", "&")
            return cover
    return None


def download_cover(cover_url, filepath):
    """下载封面图片"""
    if os.path.exists(filepath):
        return True  # 已存在
    req = urllib.request.Request(cover_url, headers=HEADERS)
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
            if resp.status == 200:
                data = resp.read()
                if len(data) > 1000:  # 至少 1KB
                    with open(filepath, "wb") as f:
                        f.write(data)
                    return True
    except Exception:
        pass
    return False


def main():
    csv_data = load_csv()
    print(f"CSV 加载 {len(csv_data)} 本书\n")

    with open(BOOKS_PATH, "r", encoding="utf-8") as f:
        books = json.load(f)

    os.makedirs(COVERS_DIR, exist_ok=True)

    updated = 0
    cover_ok = 0

    for i, book in enumerate(books):
        title = book["title"]
        info = csv_data.get(title)

        if not info:
            # 模糊匹配
            for csv_title in csv_data:
                if title in csv_title or csv_title in title:
                    info = csv_data[csv_title]
                    break

        if not info:
            print(f"[{i+1}/{len(books)}] {title} ❌ CSV 中未找到")
            continue

        # 更新元数据
        if info["author"]:
            # CSV 作者可能有额外空格和注释
            author = re.sub(r"\s+", " ", info["author"]).strip()
            # 截取主作者（去掉译者等信息）
            author = author.split(" 著")[0].split(" )")[-1] if " )" in author else author
            book["author"] = author
        if info["description"]:
            book["description"] = info["description"]
        if info["douban_url"]:
            book["doubanUrl"] = info["douban_url"]
        if info["rating"]:
            # 在 reason 末尾追加评分（如果没有的话）
            if "豆瓣评分" not in book.get("reason", ""):
                book["reason"] = book.get("reason", "") + f" 豆瓣评分{info['rating']}。"

        # 获取新封面
        douban_url = info.get("douban_url", "")
        match = re.search(r"/subject/(\d+)/", douban_url)
        if match:
            subject_id = match.group(1)
            print(f"[{i+1}/{len(books)}] {title} (subject:{subject_id}) ...", end=" ", flush=True)

            cover_url = get_cover_url(subject_id)
            if cover_url:
                ext = ".webp" if ".webp" in cover_url else ".jpg"
                filepath = os.path.join(COVERS_DIR, f"{book['id']}{ext}")
                if download_cover(cover_url, filepath):
                    local_path = f"/book-daily/covers/{book['id']}{ext}"
                    book["cover"] = local_path
                    print("✅ 封面已更新")
                    cover_ok += 1
                else:
                    print("⚠️ 封面下载失败")
            else:
                print("⚠️ 无封面")
        else:
            print(f"[{i+1}/{len(books)}] {title} ⚠️ 无豆瓣链接")

        updated += 1
        time.sleep(2)

    # 写回
    with open(BOOKS_PATH, "w", encoding="utf-8") as f:
        json.dump(books, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 完成！元数据更新 {updated}/{len(books)}, 封面更新 {cover_ok}")


if __name__ == "__main__":
    main()
