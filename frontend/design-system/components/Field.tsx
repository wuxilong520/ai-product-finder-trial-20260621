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
}: {
  id: string;
  type: string;
  value: string;
  onChange: (value: string) => void;
  label: string;
  placeholder: string;
}) {
  const [showPassword, setShowPassword] = useState(false);
  const resolvedType = useMemo(() => {
    if (type !== "password") {
      return type;
    }
    return showPassword ? "text" : "password";
  }, [showPassword, type]);

  return (
    <div className="group relative">
      <Input
        id={id}
        type={resolvedType}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder=" "
        appearance="minimal"
        className="peer h-14 px-4 pb-3 pt-5 text-lg text-slate-950 placeholder:text-transparent"
      />
      <label
        htmlFor={id}
        className="pointer-events-none absolute left-4 top-1/2 z-10 -translate-y-1/2 origin-left bg-transparent px-1 text-sm text-slate-400 transition-all duration-200 peer-focus:top-3 peer-focus:translate-y-0 peer-focus:scale-90 peer-focus:text-app-brand-secondary peer-[:not(:placeholder-shown)]:top-3 peer-[:not(:placeholder-shown)]:translate-y-0 peer-[:not(:placeholder-shown)]:scale-90"
      >
        {label}
      </label>
      {type === "password" ? (
        <button
          type="button"
          aria-label={showPassword ? "隐藏密码" : "显示密码"}
          onClick={() => setShowPassword((value) => !value)}
          className="absolute right-4 top-1/2 z-10 -translate-y-1/2 text-slate-500 transition hover:text-slate-800"
        >
          {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
        </button>
      ) : null}
      <div className="pointer-events-none absolute inset-0 rounded-2xl opacity-0 transition duration-200 group-hover:opacity-100 group-focus-within:opacity-100">
        <div className="absolute inset-0 rounded-2xl bg-[radial-gradient(circle_at_top,rgba(108,92,231,0.14),transparent_60%)]" />
      </div>
    </div>
  );
}
