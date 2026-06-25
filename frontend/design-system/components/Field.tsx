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
}: {
  id: string;
  type: string;
  value: string;
  onChange: (value: string) => void;
  label: string;
  placeholder: string;
  autoComplete?: string;
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
      <label htmlFor={id} className="block text-sm font-medium text-slate-200">
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
        className="h-14 rounded-2xl border-white/12 bg-white/8 px-4 pr-14 text-base text-[#f8fafc] placeholder:text-[rgba(248,250,252,0.42)] [color-scheme:dark] [-webkit-text-fill-color:#f8fafc] focus:border-[#6C5CE7] focus:bg-white/10 focus:shadow-[0_0_0_1px_rgba(108,92,231,0.22),0_0_28px_rgba(108,92,231,0.18)]"
        style={{
          backgroundColor: "rgba(15, 23, 42, 0.82)",
          color: "#f8fafc",
          borderColor: "rgba(255, 255, 255, 0.14)",
          WebkitTextFillColor: "#f8fafc",
          caretColor: "#f8fafc",
        }}
      />
      {type === "password" ? (
        <button
          type="button"
          aria-label={showPassword ? "隐藏密码" : "显示密码"}
          onClick={() => setShowPassword((value) => !value)}
          className="absolute right-4 top-1/2 z-20 flex h-8 w-8 -translate-y-1/2 items-center justify-center rounded-full bg-transparent text-slate-300 transition hover:bg-white/10 hover:text-white focus:outline-none focus:ring-2 focus:ring-[#6C5CE7]/45"
        >
          {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
        </button>
      ) : null}
      <div className="pointer-events-none absolute inset-0 rounded-2xl opacity-0 transition duration-200 group-hover:opacity-100 group-focus-within:opacity-100">
        <div className="absolute inset-0 rounded-2xl bg-[radial-gradient(circle_at_top,rgba(108,92,231,0.14),transparent_60%)]" />
      </div>
      </div>
    </div>
  );
}
