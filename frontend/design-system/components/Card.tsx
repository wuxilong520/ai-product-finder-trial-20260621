import * as React from "react";

import { cn } from "@/lib/utils";

const cardVariants = {
  default: "glass-card text-app-text-primary",
  elevated: "glass-card glow-border text-app-text-primary",
  panel: "glass-card-strong text-app-text-primary",
  subtle: "rounded-2xl border border-app-border bg-white/5 text-app-text-primary shadow-app-soft",
} as const;

export function Card({
  className,
  variant = "default",
  ...props
}: React.HTMLAttributes<HTMLDivElement> & { variant?: keyof typeof cardVariants }) {
  return <div className={cn(cardVariants[variant], className)} {...props} />;
}

export function CardHeader({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("flex flex-col space-y-1.5 p-6", className)} {...props} />;
}

export function CardTitle({ className, ...props }: React.HTMLAttributes<HTMLHeadingElement>) {
  return <h3 className={cn("text-lg font-semibold tracking-tight text-white", className)} {...props} />;
}

export function CardDescription({ className, ...props }: React.HTMLAttributes<HTMLParagraphElement>) {
  return <p className={cn("text-sm leading-6 text-app-text-secondary", className)} {...props} />;
}

export function CardContent({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("p-6 pt-0", className)} {...props} />;
}
