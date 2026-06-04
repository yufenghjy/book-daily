import { useState, useEffect } from "preact/hooks";

export default function ThemeToggle() {
  const [dark, setDark] = useState(false);

  // Sync state with actual DOM class on client mount
  useEffect(() => {
    setDark(document.documentElement.classList.contains("dark"));
  }, []);

  const toggle = () => {
    const next = !dark;
    setDark(next);
    document.documentElement.classList.toggle("dark", next);
    localStorage.setItem("theme", next ? "dark" : "light");
  };

  return (
    <button
      onClick={toggle}
      aria-label="切换暗色/亮色模式"
      class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700
             transition-colors text-lg leading-none"
    >
      {dark ? "☀️" : "🌙"}
    </button>
  );
}
