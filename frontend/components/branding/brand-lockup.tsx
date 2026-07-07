"use client";

import Image from "next/image";
import Link from "next/link";

import { ROUTES } from "@/config/routes";
import { cn } from "@/lib/utils";

type BrandLockupProps = {
  href?: string;
  size?: "sm" | "md" | "lg";
  showTagline?: boolean;
  darkMode?: boolean;
  className?: string;
};

const sizeMap = {
  sm: {
    card: "rounded-2xl px-2 py-1.5",
    image: { width: 112, height: 56 },
    title: "text-sm",
    desc: "text-[11px]",
    tagline: "text-[11px]",
  },
  md: {
    card: "rounded-[20px] px-3 py-2",
    image: { width: 152, height: 76 },
    title: "text-base",
    desc: "text-xs",
    tagline: "text-xs",
  },
  lg: {
    card: "rounded-[24px] px-4 py-3",
    image: { width: 228, height: 114 },
    title: "text-lg",
    desc: "text-sm",
    tagline: "text-sm",
  },
} as const;

export function BrandLockup({
  href = ROUTES.home,
  size = "md",
  showTagline = false,
  darkMode = true,
  className,
}: BrandLockupProps) {
  const current = sizeMap[size];

  return (
    <Link href={href} className={cn("inline-flex items-center gap-4", className)}>
      <div className={cn("bg-white shadow-[0_18px_45px_rgba(15,23,42,0.18)]", current.card)}>
        <Image
          src="/brand/shanghang-logo.png"
          alt="商航AI"
          width={current.image.width}
          height={current.image.height}
          priority
        />
      </div>
      <div className="min-w-0">
        <div className={cn("font-semibold tracking-tight", darkMode ? "text-white" : "text-[#0F172A]", current.title)}>商航AI</div>
        <div className={cn("mt-1", darkMode ? "text-white/55" : "text-[#475569]", current.desc)}>AI驱动的跨境商业决策系统</div>
        {showTagline ? (
          <div className={cn("mt-2", darkMode ? "text-[#D8E3FF]" : "text-[#334155]", current.tagline)}>让每一次商业选择，都有方向</div>
        ) : null}
      </div>
    </Link>
  );
}
