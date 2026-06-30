"use client";

import Link from "next/link";
import { Crown } from "lucide-react";

import { Button } from "@/design-system/components";

export function UpgradeEntry({
  label = "升级套餐",
  href = "/pricing",
  compact = false,
}: {
  label?: string;
  href?: string;
  compact?: boolean;
}) {
  return (
    <Button asChild variant="secondary" size={compact ? "sm" : "default"}>
      <Link href={href}>
        <Crown className="mr-2 h-4 w-4" />
        {label}
      </Link>
    </Button>
  );
}
