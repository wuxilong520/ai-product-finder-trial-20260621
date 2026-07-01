"use client";

import Link from "next/link";
import type { ReactNode } from "react";

import { UpgradeEntry } from "@/components/billing/upgrade-entry";
import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { Badge, Button, Card, CardContent, CardHeader, CardTitle, EmptyState, InfoTile, StatusAlert } from "@/design-system/components";
import { ROUTES, taskDetailRoute } from "@/config/routes";
import { Language } from "@/lib/i18n";

type MetricItem = {
  label: string;
  value: string;
};

type HighlightItem = {
  title: string;
  description: string;
  href?: string;
  hrefLabel?: string;
  badge?: string;
};

export function TaskDrivenPageShell({
  lang,
  activePath,
  title,
  description,
  badge,
  notice,
  metrics,
  highlights,
  currentTaskId,
  children,
}: {
  lang: Language;
  activePath: "products" | "insights" | "action" | "settings";
  title: string;
  description: string;
  badge: string;
  notice: string;
  metrics: MetricItem[];
  highlights: HighlightItem[];
  currentTaskId?: number;
  children?: ReactNode;
}) {
  return (
    <XBorderLayout lang={lang} activePath={activePath}>
      <div className="space-y-6">
        <Card variant="panel" className="p-6">
          <div className="flex flex-col gap-5 md:flex-row md:items-start md:justify-between">
            <div className="max-w-3xl">
              <Badge variant="brand">{badge}</Badge>
              <h1 className="mt-4 text-3xl font-semibold tracking-tight text-white">{title}</h1>
              <p className="mt-3 text-sm leading-7 text-app-text-secondary">{description}</p>
            </div>
            <div className="flex flex-wrap gap-3">
              <UpgradeEntry label="升级 / 充值" />
              <Button asChild>
                <Link href={ROUTES.createTask}>发起新任务</Link>
              </Button>
            </div>
          </div>
        </Card>

        <StatusAlert status="warning" title="当前真实边界" message={notice} />

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {metrics.map((item) => (
            <InfoTile key={`${item.label}-${item.value}`} label={item.label} value={item.value} />
          ))}
        </div>

        <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <CardHeader className="flex flex-row items-center justify-between gap-4">
            <div>
              <CardTitle>当前页面能直接用什么</CardTitle>
              <p className="text-sm text-white/50">不做假入口，直接把现在能用的任务链路给你。</p>
            </div>
            {currentTaskId ? (
              <Button asChild variant="secondary">
                <Link href={taskDetailRoute(currentTaskId)}>进入最新任务</Link>
              </Button>
            ) : null}
          </CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {highlights.length ? (
              highlights.map((item) => (
                <div key={`${item.title}-${item.description}`} className="rounded-2xl border border-white/8 bg-white/[0.03] p-4">
                  <div className="flex items-start justify-between gap-3">
                    <h3 className="text-base font-semibold text-white">{item.title}</h3>
                    {item.badge ? <Badge variant="neutral">{item.badge}</Badge> : null}
                  </div>
                  <p className="mt-3 text-sm leading-7 text-white/60">{item.description}</p>
                  {item.href && item.hrefLabel ? (
                    <Button asChild size="sm" className="mt-4">
                      <Link href={item.href}>{item.hrefLabel}</Link>
                    </Button>
                  ) : null}
                </div>
              ))
            ) : (
              <EmptyState text="当前还没有可展示的数据。先发起一个任务，系统跑完后这里会自动有内容。" />
            )}
          </CardContent>
        </Card>

        {children}
      </div>
    </XBorderLayout>
  );
}
