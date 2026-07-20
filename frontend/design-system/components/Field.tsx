"use client";

import { Eye, EyeOff } from "lucide-react";
import { useMemo, useState } from "react";

import { Input } from "@/design-system/components/Input";

export function MinimalField({
  id,
  type,
  value,
  onChange,
  label,
  placeholder,
  autoComplete,
  tone = "dark",
}: {
  id: string;
  type: string;
  value: string;
  onChange: (value: string) => void;
  label: string;
  placeholder: string;
  autoComplete?: string;
  tone?: "dark" | "light";
}) {
  const [showPassword, setShowPassword] = useState(false);
  const resolvedType = useMemo(() => {
    if (type !== "password") {
      return type;
    }
    return showPassword ? "text" : "password";
  }, [showPassword, type]);

  return (
    <div className="group space-y-2">
      <label htmlFor={id} className={type === "password" || tone === "dark" ? "block text-sm font-medium text-[#E2E8F0]" : "block text-sm font-medium text-[#334155]"}>
        {label}
      </label>
      <div className="relative">
      <Input
        id={id}
        type={resolvedType}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        autoComplete={autoComplete ?? "off"}
        autoCorrect="off"
        autoCapitalize="none"
        spellCheck={false}
        appearance="minimal"
        className={
          tone === "light"
            ? "h-14 rounded-2xl border-[#E7E5E4] bg-[#FFFDF8] px-4 pr-14 text-base text-[#1F2937] placeholder:text-[#9CA3AF] focus:border-[#F97316] focus:bg-white focus:shadow-[0_0_0_1px_rgba(249,115,22,0.18),0_0_24px_rgba(251,146,60,0.12)]"
            : "h-14 rounded-2xl border-white/12 bg-white/8 px-4 pr-14 text-base text-[#f8fafc] placeholder:text-[rgba(248,250,252,0.42)] [color-scheme:dark] [-webkit-text-fill-color:#f8fafc] focus:border-[#6C5CE7] focus:bg-white/10 focus:shadow-[0_0_0_1px_rgba(108,92,231,0.22),0_0_28px_rgba(108,92,231,0.18)]"
        }
        style={{
          backgroundColor: tone === "light" ? "#FFFDF8" : "rgba(15, 23, 42, 0.82)",
          color: tone === "light" ? "#1F2937" : "#f8fafc",
          borderColor: tone === "light" ? "#E7E5E4" : "rgba(255, 255, 255, 0.14)",
          WebkitTextFillColor: tone === "light" ? "#1F2937" : "#f8fafc",
          caretColor: tone === "light" ? "#1F2937" : "#f8fafc",
        }}
      />
      {type === "password" ? (
        <button
          type="button"
          aria-label={showPassword ? "隐藏密码" : "显示密码"}
          onClick={() => setShowPassword((value) => !value)}
          className={
            tone === "light"
              ? "absolute right-4 top-1/2 z-20 flex h-8 w-8 -translate-y-1/2 items-center justify-center rounded-full bg-transparent text-[#94A3B8] transition hover:bg-[#FFF3E8] hover:text-[#EA580C] focus:outline-none focus:ring-2 focus:ring-[#F97316]/30"
              : "absolute right-4 top-1/2 z-20 flex h-8 w-8 -translate-y-1/2 items-center justify-center rounded-full bg-transparent text-[#CBD5E1] transition hover:bg-white/10 hover:text-white focus:outline-none focus:ring-2 focus:ring-[#6C5CE7]/45"
          }
        >
          {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
        </button>
      ) : null}
      <div className="pointer-events-none absolute inset-0 rounded-2xl opacity-0 transition duration-200 group-hover:opacity-100 group-focus-within:opacity-100">
        <div
          className={
            tone === "light"
              ? "absolute inset-0 rounded-2xl bg-[radial-gradient(circle_at_top,rgba(249,115,22,0.12),transparent_60%)]"
              : "absolute inset-0 rounded-2xl bg-[radial-gradient(circle_at_top,rgba(108,92,231,0.14),transparent_60%)]"
          }
        />
      </div>
      </div>
    </div>
  );
}
