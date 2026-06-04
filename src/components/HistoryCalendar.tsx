import { useState } from "preact/hooks";
import type { Book } from "../lib/daily";
import { getDailyBook } from "../lib/daily";

interface Props {
  books: Book[];
  initialYear: number;
  initialMonth: number; // 1-12
  base: string;
}

const WEEKDAYS = ["日", "一", "二", "三", "四", "五", "六"];

export default function HistoryCalendar({
  books,
  initialYear,
  initialMonth,
  base,
}: Props) {
  const [year, setYear] = useState(initialYear);
  const [month, setMonth] = useState(initialMonth);

  const todayStr = new Date().toISOString().slice(0, 10);

  const daysInMonth = new Date(year, month, 0).getDate();
  const firstDayOfWeek = new Date(year, month - 1, 1).getDay(); // 0=Sun

  const prevMonth = () => {
    if (month === 1) {
      setYear(year - 1);
      setMonth(12);
    } else {
      setMonth(month - 1);
    }
  };

  const nextMonth = () => {
    if (month === 12) {
      setYear(year + 1);
      setMonth(1);
    } else {
      setMonth(month + 1);
    }
  };

  const goToday = () => {
    const now = new Date();
    setYear(now.getFullYear());
    setMonth(now.getMonth() + 1);
  };

  // Build calendar grid
  const cells: { dateStr: string; day: number; isPlaceholder: boolean }[] = [];

  // Placeholders for days before the 1st
  for (let i = 0; i < firstDayOfWeek; i++) {
    cells.push({ dateStr: "", day: 0, isPlaceholder: true });
  }

  // Actual days
  for (let day = 1; day <= daysInMonth; day++) {
    const mm = String(month).padStart(2, "0");
    const dd = String(day).padStart(2, "0");
    cells.push({
      dateStr: `${year}-${mm}-${dd}`,
      day,
      isPlaceholder: false,
    });
  }

  return (
    <div class="select-none">
      {/* Month navigation */}
      <div class="flex items-center justify-between mb-4">
        <button
          onClick={prevMonth}
          class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700
                 transition-colors text-lg"
          aria-label="上个月"
        >
          ←
        </button>
        <h2 class="text-xl font-bold">
          {year} 年 {month} 月
        </h2>
        <button
          onClick={nextMonth}
          class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700
                 transition-colors text-lg"
          aria-label="下个月"
        >
          →
        </button>
      </div>

      {/* Weekday header */}
      <div class="grid grid-cols-7 gap-1 mb-2">
        {WEEKDAYS.map((w) => (
          <div
            class="text-center text-xs font-medium text-gray-500
                   dark:text-gray-400 py-1"
          >
            {w}
          </div>
        ))}
      </div>

      {/* Calendar grid */}
      <div class="grid grid-cols-7 gap-1">
        {cells.map((cell) => {
          if (cell.isPlaceholder) {
            return <div class="aspect-square" />;
          }

          const book = getDailyBook(books, cell.dateStr);
          const isToday = cell.dateStr === todayStr;

          return (
            <a
              href={`${base}${cell.dateStr}`}
              class={`aspect-square flex flex-col items-center justify-center
                      rounded-lg text-sm transition-colors relative
                      ${
                        isToday
                          ? "bg-blue-500 text-white font-bold shadow-md"
                          : "hover:bg-gray-100 dark:hover:bg-gray-700"
                      }`}
              title={`${cell.dateStr}: ${book.title}`}
            >
              <span>{cell.day}</span>
              <span class="text-[10px] leading-tight text-center px-0.5 truncate max-w-full">
                {book.title}
              </span>
            </a>
          );
        })}
      </div>

      {/* Today button */}
      <div class="text-center mt-4">
        <button
          onClick={goToday}
          class="text-sm px-4 py-2 rounded-lg
                 bg-gray-100 dark:bg-gray-700
                 hover:bg-gray-200 dark:hover:bg-gray-600
                 transition-colors"
        >
          回到今天
        </button>
      </div>
    </div>
  );
}
