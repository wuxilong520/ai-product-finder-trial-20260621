"use client";

import { useRouter } from "next/navigation";

import { LANGUAGE_COOKIE, Language } from "@/lib/i18n";
import { cn } from "@/lib/utils";

export function LanguageToggle({ lang }: { lang: Language }) {
  const router = useRouter();

  function switchLanguage(nextLang: Language) {
    document.cookie = `${LANGUAGE_COOKIE}=${nextLang}; path=/; max-age=${60 * 60 * 24 * 365}`;
    router.refresh();
    window.location.reload();
  }

  return (
    <div className="inline-flex items-center gap-1 rounded-full border border-[#F3E8D8] bg-white p-1 shadow-[0_18px_40px_rgba(15,23,42,0.1)]">
      {(["zh", "en"] as const).map((item) => {
        const active = lang === item;
        return (
          <button
            key={item}
            type="button"
            onClick={() => switchLanguage(item)}
            className={cn(
              "rounded-full px-3 py-1.5 text-sm font-medium transition",
              active
                ? "bg-[linear-gradient(135deg,#7C3AED,#06B6D4)] text-white shadow-[0_16px_34px_rgba(59,130,246,0.24)]"
                : "text-[#94A3B8] hover:bg-[#FFF7ED] hover:text-[#475569]"
            )}
          >
            {item === "zh" ? "中文" : "EN"}
          </button>
        );
      })}
    </div>
  );
}
