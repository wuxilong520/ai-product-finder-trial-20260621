"use client";

import Link from "next/link";
import type { ReactNode } from "react";

import { UpgradeEntry } from "@/components/billing/upgrade-entry";
import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { Button, Card, CardContent, CardHeader, CardTitle, InfoTile } from "@/design-system/components";
import { ROUTES } from "@/config/routes";
import { Language } from "@/lib/i18n";

type HonestStatusPageProps = {
  lang: Language;
  activePath: "products" | "insights" | "action" | "settings";
  title: string;
  description: string;
  statusLabel: string;
  statusValue: string;
  currentLabel: string;
  currentValue: string;
  nextLabel: string;
  nextValue: string;
  children?: ReactNode;
};

export function HonestStatusPage(props: HonestStatusPageProps) {
  const { lang, activePath, title, description, statusLabel, statusValue, currentLabel, currentValue, nextLabel, nextValue, children } = props;

  return (
    <XBorderLayout lang={lang} activePath={activePath}>
      <div className="space-y-6">
        <Card className="border-white/8 bg-[#121c2c] p-6 shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <h1 className="text-3xl font-semibold tracking-tight text-white">{title}</h1>
              <p className="mt-2 text-sm leading-7 text-white/60">{description}</p>
            </div>
            <UpgradeEntry label="升级 / 充值" />
          </div>
        </Card>

        <div className="grid gap-6 md:grid-cols-3">
          <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader><CardTitle>当前状态</CardTitle></CardHeader>
            <CardContent><InfoTile label={statusLabel} value={statusValue} /></CardContent>
          </Card>
          <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader><CardTitle>现在能做什么</CardTitle></CardHeader>
            <CardContent><InfoTile label={currentLabel} value={currentValue} /></CardContent>
          </Card>
          <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader><CardTitle>后续会补什么</CardTitle></CardHeader>
            <CardContent><InfoTile label={nextLabel} value={nextValue} /></CardContent>
          </Card>
        </div>

        <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <CardHeader><CardTitle>下一步入口</CardTitle></CardHeader>
          <CardContent className="flex flex-wrap gap-3">
            <Button asChild><Link href={ROUTES.createTask}>去发起任务</Link></Button>
            <Button asChild variant="outline"><Link href={ROUTES.tasks}>查看任务结果</Link></Button>
            <Button asChild variant="secondary"><Link href={ROUTES.pricing}>查看套餐权限</Link></Button>
            {children}
          </CardContent>
        </Card>
      </div>
    </XBorderLayout>
  );
}
