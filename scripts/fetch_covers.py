"""
从豆瓣获取书籍正确封面 URL
用法: python scripts/fetch_covers.py
如缺少 requests 库: pip install requests
"""
import json, time, re, ssl

BOOKS_PATH = "src/data/books.json"

# 模拟真实浏览器
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
}


def fetch(url):
    """使用 requests 或 urllib 获取网页"""
    try:
        import requests
        resp = requests.get(url, headers=HEADERS, timeout=15)
        return resp.text
    except ImportError:
        pass

    # fallback to urllib with SSL context
    import urllib.request
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            if resp.headers.get("Content-Encoding") == "gzip":
                import gzip
                return gzip.decompress(resp.read()).decode("utf-8")
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        raise e


def search_douban(title):
    """搜索豆瓣并返回 subject_id 和 封面图URL"""
    import urllib.parse
    query = urllib.parse.quote(title)
    url = f"https://www.douban.com/search?cat=1001&q={query}"

    try:
        html = fetch(url)
    except Exception as e:
        print(f"  ❌ 搜索失败: {e}")
        return None, None

    # 提取第一个书籍 subject ID
    match = re.search(r'https://book\.douban\.com/subject/(\d+)/', html)
    if not match:
        match = re.search(r'sid:\s*(\d+)', html)
    if not match:
        # 尝试从 onclick 属性提取
        match = re.search(r'/subject/(\d+)/', html)
    if not match:
        print(f"  ⚠️ 未找到豆瓣条目")
        return None, None

    subject_id = match.group(1)

    # 访问书籍页面获取封面
    book_url = f"https://book.douban.com/subject/{subject_id}/"
    try:
        html2 = fetch(book_url)
    except Exception as e:
        print(f"  ❌ 获取详情页失败: {e}")
        return subject_id, None

    # 提取封面图 (多种策略)
    cover_url = None
    for pattern in [
        r'"pic"\s*:\s*"([^"]+)"',
        r'<meta\s+property="og:image"\s+content="([^"]+)"',
        r'<img[^>]*src="([^"]*view/subject/[^"]*public[^"]+)"',
        r'data-cover="([^"]+)"',
    ]:
        m = re.search(pattern, html2)
        if m:
            cover_url = m.group(1)
            break

    return subject_id, cover_url


def main():
    with open(BOOKS_PATH, "r", encoding="utf-8") as f:
        books = json.load(f)

    print(f"共 {len(books)} 本书，开始获取封面...\n")
    updated = 0

    for i, book in enumerate(books):
        title = book["title"]
        print(f"[{i+1}/{len(books)}] {title} ...", end=" ", flush=True)

        subject_id, cover_url = search_douban(title)

        if cover_url:
            # 统一使用大图
            cover_url = cover_url.replace("/m/", "/l/").replace("/s/", "/l/")
            # 处理 URL 编码
            cover_url = cover_url.replace("&amp;", "&")
            book["cover"] = cover_url
            if subject_id:
                book["doubanUrl"] = f"https://book.douban.com/subject/{subject_id}/"
            print(f"✅")
            updated += 1
        elif subject_id:
            book["doubanUrl"] = f"https://book.douban.com/subject/{subject_id}/"
            print(f"⚠️ 有条目无封面")
        else:
            print(f"❌")

        time.sleep(2)  # 避免被限制

    with open(BOOKS_PATH, "w", encoding="utf-8") as f:
        json.dump(books, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 完成！{updated}/{len(books)} 本封面已更新")


if __name__ == "__main__":
    main()
