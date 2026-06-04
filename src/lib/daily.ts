export interface Book {
  id: string;
  title: string;
  author: string;
  cover: string;
  description: string;
  reason: string;
  category: string;
  doubanUrl?: string;
}

/**
 * DJB2 hash algorithm: date string → deterministic integer seed.
 * Same date always produces same seed, different dates scatter well.
 */
export function dateToSeed(dateStr: string): number {
  let hash = 5381;
  const str = dateStr.replace(/-/g, "");
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) + hash) + str.charCodeAt(i);
    hash |= 0; // force 32-bit int
  }
  return Math.abs(hash);
}

/**
 * Get the daily book for a given date.
 * Books are sorted by id for deterministic ordering before selection.
 */
export function getDailyBook(books: Book[], dateStr: string): Book {
  if (books.length === 0) {
    throw new Error("书籍列表为空，无法选择推荐");
  }
  const sorted = [...books].sort((a, b) => Number(a.id) - Number(b.id));
  const seed = dateToSeed(dateStr);
  return sorted[seed % sorted.length];
}

/**
 * Format date string for display, e.g. "2026-06-04" → "2026年6月4日"
 */
export function formatDateCN(dateStr: string): string {
  const d = new Date(dateStr + "T00:00:00");
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`;
}

/**
 * Get "today" string in YYYY-MM-DD format using Asia/Shanghai timezone
 */
export function getTodayStr(): string {
  const now = new Date();
  // Use Asia/Shanghai timezone
  const formatter = new Intl.DateTimeFormat("zh-CN", {
    timeZone: "Asia/Shanghai",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  });
  const parts = formatter.formatToParts(now);
  const y = parts.find((p) => p.type === "year")!.value;
  const m = parts.find((p) => p.type === "month")!.value;
  const d = parts.find((p) => p.type === "day")!.value;
  return `${y}-${m}-${d}`;
}
