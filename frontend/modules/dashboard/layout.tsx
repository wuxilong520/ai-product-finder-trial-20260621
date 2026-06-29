"use client";

import type { ReactNode } from "react";
import Link from "next/link";
import { Bell, ChevronDown, ChevronRight, LayoutDashboard, Menu, Settings, Sparkles } from "lucide-react";
import { usePathname } from "next/navigation";

import { ROUTES } from "@/config/routes";
import { Card } from "@/design-system/components";
import { LanguageToggle } from "@/design-system/components/LanguageToggle";
import { Button } from "@/design-system/components/Button";
import { getFlowActiveFromPath } from "@/components/decision-flow/decision-flow-shell";
import { Language, t } from "@/lib/i18n";
import { cn } from "@/lib/utils";

type DashboardText = ReturnType<typeof t>;
type DashboardTextKey = keyof DashboardText;

type DashboardLayoutProps = {
  children: ReactNode;
  rightRail?: ReactNode;
  lang: Language;
  activePath?: "dashboard" | "crawl" | "analyze" | "products" | "p5" | "market" | "supplier" | "operation" | "admin" | "settings";
};

const navSections = [
  {
    titleKey: "navHome" as DashboardTextKey,
    items: [{ key: "dashboard", href: ROUTES.dashboard, icon: LayoutDashboard, label: "决策流" }],
  },
  {
    titleKey: "navProductHub" as DashboardTextKey,
    items: [{ key: "products", href: ROUTES.products, icon: Sparkles, label: "商品中心" }],
  },
  {
    titleKey: "navSystemAdmin" as DashboardTextKey,
    items: [{ key: "admin", href: ROUTES.systemAdmin, icon: Settings, label: "系统设置" }],
  },
];

const topTabs = [
  { key: "crawl", label: "① 采集", href: ROUTES.crawl },
  { key: "analyze", label: "② 分析", href: ROUTES.analyze },
  { key: "market", label: "③ 市场", href: ROUTES.marketAnalysis },
  { key: "supplier", label: "④ 供应链", href: ROUTES.supplier },
  { key: "dashboard", label: "⑤ 决策", href: ROUTES.dashboard },
  { key: "operation", label: "⑥ 执行", href: ROUTES.operation },
];

export function NewDashboardLayout({ children, rightRail, lang, activePath = "dashboard" }: DashboardLayoutProps) {
  const text = t(lang);
  const pathname = usePathname();
  const flowNavKey = getFlowActiveFromPath(pathname || "/dashboard");
  const navActivePath = activePath === "crawl" || activePath === "analyze" || activePath === "market" || activePath === "supplier" || activePath === "operation" || activePath === "p5"
    ? "dashboard"
    : activePath === "settings"
      ? "admin"
      : activePath;

  return (
    <div className="min-h-screen bg-[#060d18] text-white">
      <div className="mx-auto flex min-h-screen max-w-[1760px]">
        <aside className="w-[295px] shrink-0 border-r border-white/10 bg-[linear-gradient(180deg,#08101c_0%,#09121f_100%)] px-6 py-8">
          <div className="flex items-center justify-between gap-4 px-2 pb-8">
            <div className="flex min-w-0 items-center gap-3.5">
              <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-[linear-gradient(135deg,#2563eb,#6d28d9)] text-white shadow-[0_0_26px_rgba(59,130,246,0.22)]">
                <Sparkles className="h-4 w-4" />
              </div>
              <div className="min-w-0">
                <div className="text-[18px] font-semibold leading-none tracking-tight text-white">XBorder</div>
                <div className="mt-2 truncate text-[14px] text-white/55">{lang === "zh" ? "AI单决策流系统" : "AI decision flow system"}</div>
              </div>
            </div>
            <button className="flex h-[50px] w-[50px] shrink-0 items-center justify-center rounded-2xl border border-white/10 bg-white/[0.03] text-white/60 shadow-[0_10px_20px_rgba(0,0,0,0.16)]">
              <Menu className="h-4 w-4" />
            </button>
          </div>

          <div className="mt-1 space-y-9">
            {navSections.map((section) => (
              <div key={section.titleKey}>
                <div className="mb-4 px-2 text-[15px] font-semibold tracking-wide text-white/95">{text[section.titleKey]}</div>
                <div className="space-y-3">
                  {section.items.map((item) => {
                    const Icon = item.icon;
                    const active = item.key === flowNavKey || item.key === navActivePath;
                    const label = item.label;
                    return (
                      <Link
                        key={`${section.titleKey}-${item.key}`}
                        href={item.href}
                        className={cn(
                          "group flex items-center justify-between rounded-[24px] px-4 py-3.5 text-[17px] transition-all duration-150",
                          active
                            ? "border border-white/12 bg-[#121b2b] text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.04),0_16px_32px_rgba(17,24,39,0.34)]"
                            : "border border-transparent text-white/62 hover:border-white/8 hover:bg-white/[0.035] hover:text-white"
                        )}
                      >
                        <div className="flex items-center gap-4">
                          <div
                            className={cn(
                              "flex h-[56px] w-[56px] items-center justify-center rounded-[20px] border transition",
                              active
                                ? "border-white/15 bg-[#0d1628] text-white"
                                : "border-white/10 bg-white/[0.025] text-white/72 group-hover:border-white/14"
                            )}
                          >
                            <Icon className="h-5 w-5" />
                          </div>
                          <span className="font-medium">{label}</span>
                        </div>
                        <ChevronRight className={cn("h-5 w-5", active ? "text-white/85" : "text-white/30")} />
                      </Link>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>

          <Card className="mt-12 rounded-[34px] border border-white/8 bg-[linear-gradient(180deg,rgba(255,255,255,0.05),rgba(255,255,255,0.025))] p-7 shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <div className="text-[18px] font-semibold">{text.navUpgradeTitle}</div>
            <ul className="mt-6 space-y-3.5 text-[15px] text-white/72">
              <li>• {text.navUpgradeFeature1}</li>
              <li>• {text.navUpgradeFeature2}</li>
              <li>• {text.navUpgradeFeature3}</li>
            </ul>
            <Button className="mt-8 h-16 w-full rounded-[24px] text-base">{text.navUpgradeAction}</Button>
          </Card>
        </aside>

        <div className="min-w-0 flex-1 bg-[radial-gradient(circle_at_top,rgba(37,99,235,0.08),transparent_24%),linear-gradient(180deg,#09111f,#07101c)]">
          <header className="border-b border-white/10 bg-[#08111d]/95 px-8 py-8 backdrop-blur-xl xl:px-10">
            <div className="flex flex-col gap-7">
              <nav className="flex min-w-0 items-center gap-9 overflow-x-auto text-[18px]">
                {topTabs.map((tab) => {
                  const active = tab.key === activePath;
                  const content = (
                    <span
                      className={cn(
                        "relative whitespace-nowrap pb-3 transition",
                        active ? "font-semibold text-white after:absolute after:bottom-0 after:left-0 after:h-[3px] after:w-full after:rounded-full after:bg-[#2d6cff]" : "text-white/58 hover:text-white/80"
                      )}
                    >
                      {tab.label}
                    </span>
                  );
                  return (
                    <Link key={tab.key} href={tab.href}>
                      {content}
                    </Link>
                  );
                })}
              </nav>

              <div className="flex flex-wrap items-center gap-4">
                <div className="rounded-full border border-white/10 bg-white/[0.02] p-1.5 shadow-[0_10px_24px_rgba(0,0,0,0.14)]">
                  <LanguageToggle lang={lang} />
                </div>
                <div className="flex h-[58px] items-center gap-2 rounded-full border border-white/10 bg-white/[0.03] px-6 text-base text-white/78 shadow-[0_10px_24px_rgba(0,0,0,0.14)]">
                  <span className="text-base">🇺🇸</span>
                  {text.navMarketLabel}
                  <ChevronDown className="h-4 w-4 text-white/40" />
                </div>
                <button className="flex h-[58px] w-[58px] items-center justify-center rounded-full border border-white/10 bg-white/[0.03] text-white/70 shadow-[0_10px_24px_rgba(0,0,0,0.14)]">
                  <Bell className="h-4 w-4" />
                </button>
              </div>
            </div>
          </header>

          <div className="flex min-h-[calc(100vh-110px)] gap-6 px-8 py-8 xl:px-10 xl:py-9">
            <main className="min-w-0 flex-1">{children}</main>
            {rightRail ? <aside className="w-[392px] shrink-0 space-y-6">{rightRail}</aside> : null}
          </div>
        </div>
      </div>
    </div>
  );
}
