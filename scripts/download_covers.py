"""
下载书籍封面图片到 public/covers/ 目录
用法: python scripts/download_covers.py
"""
import json, os, time, urllib.request, ssl

BOOKS_PATH = "src/data/books.json"
COVERS_DIR = "public/covers"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://book.douban.com/",
}


def download(url, filepath):
    """下载图片到本地"""
    req = urllib.request.Request(url, headers=HEADERS)
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
            if resp.status == 200:
                with open(filepath, "wb") as f:
                    f.write(resp.read())
                return True
    except Exception as e:
        print(f"    下载失败: {e}")
    return False


def main():
    os.makedirs(COVERS_DIR, exist_ok=True)

    with open(BOOKS_PATH, "r", encoding="utf-8") as f:
        books = json.load(f)

    print(f"共 {len(books)} 本书，开始下载封面...\n")
    ok, fail = 0, 0

    for i, book in enumerate(books):
        title = book["title"]
        cover_url = book.get("cover", "")
        ext = ".jpg" if ".jpg" in cover_url else ".png" if ".png" in cover_url else ".jpg"
        filepath = os.path.join(COVERS_DIR, f"{book['id']}{ext}")
        local_path = f"/book-daily/covers/{book['id']}{ext}"

        print(f"[{i+1}/{len(books)}] {title} ...", end=" ", flush=True)

        if not cover_url:
            print("❌ 无封面 URL")
            fail += 1
            continue

        if download(cover_url, filepath):
            # 检查文件大小（太小可能是错误图片）
            size = os.path.getsize(filepath)
            if size < 1000:
                print(f"⚠️ 图片太小({size}B)，可能无效")
                fail += 1
                continue
            book["cover"] = local_path
            print(f"✅ ({size//1024}KB)")
            ok += 1
        else:
            print(f"❌")
            fail += 1

        time.sleep(0.5)

    # 写回
    with open(BOOKS_PATH, "w", encoding="utf-8") as f:
        json.dump(books, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 完成！成功 {ok}, 失败 {fail}")
    if fail > 0:
        print("失败的书需要手动找正确封面 URL，替换 books.json 里的 cover 字段后重新运行此脚本。")


if __name__ == "__main__":
    main()
