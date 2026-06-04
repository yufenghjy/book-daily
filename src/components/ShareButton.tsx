import { useState } from "preact/hooks";

interface Props {
  title: string;
  date?: string;
  base?: string;
}

export default function ShareButton({ title, date, base = "" }: Props) {
  const [copied, setCopied] = useState(false);

  const getUrl = () =>
    date
      ? `${window.location.origin}${base}${date}`
      : window.location.href;

  const shareText = `📚 今日推荐：《${title}》`;

  const handleShare = async () => {
    const url = getUrl();
    // Try Web Share API first (mobile friendly)
    if (navigator.share) {
      try {
        await navigator.share({
          title: shareText,
          text: shareText,
          url,
        });
        return;
      } catch (e) {
        if ((e as DOMException).name === "AbortError") return;
        // Fall through to clipboard fallback on error
      }
    }

    // Fallback: copy to clipboard
    try {
      await navigator.clipboard.writeText(`${shareText}\n${url}`);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Last resort: prompt
      prompt("复制此链接分享:", url);
    }
  };

  return (
    <button
      onClick={handleShare}
      class="inline-flex items-center gap-1 px-4 py-2 text-sm rounded-lg
             bg-gray-100 dark:bg-gray-700
             hover:bg-gray-200 dark:hover:bg-gray-600
             transition-colors"
    >
      {copied ? "✓ 已复制链接" : "📤 分享"}
    </button>
  );
}
