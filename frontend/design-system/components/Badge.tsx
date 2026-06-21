import * as React from "react";

import { cn } from "@/lib/utils";

const variantMap = {
  neutral: "border border-white/10 bg-white/8 text-app-text-secondary",
  brand: "border border-cyan-400/20 bg-cyan-400/12 text-cyan-300",
  running: "border border-teal-400/20 bg-teal-400/12 text-teal-300 shadow-[0_0_24px_rgba(20,184,166,0.15)]",
  success: "border border-emerald-400/20 bg-emerald-400/12 text-emerald-300",
  error: "border border-rose-400/20 bg-rose-400/12 text-rose-300",
  warning: "border border-amber-400/20 bg-amber-400/12 text-amber-300",
  blocked: "border border-slate-400/20 bg-slate-400/12 text-slate-300",
  blue: "border border-cyan-400/20 bg-cyan-400/12 text-cyan-300",
  destructive: "border border-rose-400/20 bg-rose-400/12 text-rose-300",
} as const;

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: keyof typeof variantMap;
  dot?: boolean;
}

export function Badge({ className, variant = "neutral", dot = false, children, ...props }: BadgeProps) {
  return (
    <div
      className={cn(
        "inline-flex items-center gap-2 rounded-full px-3 py-1.5 text-xs font-medium backdrop-blur transition",
        variantMap[variant],
        className
      )}
      {...props}
    >
      {dot ? <span className="h-2 w-2 rounded-full bg-current opacity-90" /> : null}
      {children}
    </div>
  );
}

export function StatusBadge({
  status,
  label,
  className,
}: {
  status: "running" | "success" | "error" | "warning" | "blocked";
  label: string;
  className?: string;
}) {
  return (
    <Badge variant={status} dot className={className}>
      {label}
    </Badge>
  );
}
