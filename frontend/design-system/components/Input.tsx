import * as React from "react";

import { cn } from "@/lib/utils";

const appearanceMap = {
  default:
    "border border-white/10 bg-white/5 text-white placeholder:text-app-text-muted focus:border-[#6C5CE7]/50 focus:bg-white/8 focus:shadow-[0_0_0_1px_rgba(108,92,231,0.18),0_0_28px_rgba(108,92,231,0.18)]",
  minimal:
    "border border-white/8 bg-white/[0.03] text-white placeholder:text-transparent focus:border-[#6C5CE7]/45 focus:bg-white/[0.06] focus:shadow-[0_0_0_1px_rgba(108,92,231,0.16),0_0_24px_rgba(108,92,231,0.18)]",
} as const;

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  appearance?: keyof typeof appearanceMap;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(({ className, appearance = "default", ...props }, ref) => {
  return (
    <input
      className={cn(
        "flex h-12 w-full rounded-2xl px-4 py-2 text-sm outline-none transition duration-200",
        appearanceMap[appearance],
        className
      )}
      ref={ref}
      {...props}
    />
  );
});

Input.displayName = "Input";

export { Input };
