/**
 * 浏览器控制台脚本 —— 在豆瓣读书页面获取封面图片 URL
 *
 * 使用方法：
 * 1. 浏览器打开 https://book.douban.com/subject/1007305/ （任意一本书的豆瓣页面）
 * 2. F12 打开开发者工具 → Console
 * 3. 粘贴此脚本，修改下面的 BOOKS 数组为你的书单
 * 4. 回车运行，它会逐个打开每本书的豆瓣页，提取封面 URL
 * 5. 最后输出 JSON，复制替换 books.json
 *
 * 注意：浏览器可能会拦截新窗口，需要允许弹窗。
 */

// ====== 粘贴你的 books.json 内容到这里 ======
const BOOKS_JSON = `[
  {"id":"1","title":"百年孤独","author":"加西亚·马尔克斯"},
  {"id":"2","title":"1984","author":"乔治·奥威尔"}
]`;
// ============================================

async function fetchCover(book) {
  // 搜索豆瓣
  const searchUrl = `https://www.douban.com/search?cat=1001&q=${encodeURIComponent(book.title)}`;
  const resp = await fetch(searchUrl);
  const html = await resp.text();

  // 提取 subject id
  const match = html.match(/https:\/\/book\.douban\.com\/subject\/(\d+)\//);
  if (!match) {
    console.log(`❌ ${book.title}: 未找到`);
    return book;
  }

  const sid = match[1];
  book.doubanUrl = `https://book.douban.com/subject/${sid}/`;

  // 获取书籍详情页
  const resp2 = await fetch(book.doubanUrl);
  const html2 = await resp2.text();

  // 提取封面 URL
  const coverMatch = html2.match(/"pic"\s*:\s*"([^"]+)"/);
  if (coverMatch) {
    const url = coverMatch[1].replace(/\/[ms]\//, '/l/');
    book.cover = url;
    console.log(`✅ ${book.title}: ${url}`);
  } else {
    console.log(`⚠️ ${book.title}: 有条目${sid}，无封面`);
  }

  return book;
}

async function main() {
  const books = JSON.parse(BOOKS_JSON);
  console.log(`共 ${books.length} 本书，开始抓取...`);

  const results = [];
  for (let i = 0; i < books.length; i++) {
    console.log(`[${i+1}/${books.length}] ${books[i].title}...`);
    results.push(await fetchCover(books[i]));
    // 逐个打开新窗口的方式（备选：手动）
    await new Promise(r => setTimeout(r, 1000)); // 等 1 秒
  }

  console.log('\n===== 结果 =====');
  console.log(JSON.stringify(results, null, 2));
  console.log('\n复制上面的 JSON，替换 books.json');
}

main();
