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
    <div className="inline-flex items-center gap-1 rounded-full border border-app-border bg-white/6 p-1 backdrop-blur-xl shadow-app-soft">
      {(["zh", "en"] as const).map((item) => {
        const active = lang === item;
        return (
          <button
            key={item}
            type="button"
            onClick={() => switchLanguage(item)}
            className={cn(
              "rounded-full px-3 py-1.5 text-sm font-medium transition",
              active ? "bg-app-brand-gradient text-white shadow-app-glow" : "text-app-text-secondary hover:bg-white/8 hover:text-white"
            )}
          >
            {item === "zh" ? "中文" : "EN"}
          </button>
        );
      })}
    </div>
  );
}
