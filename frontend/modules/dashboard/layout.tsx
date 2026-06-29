"use client";

import type { ReactNode } from "react";
import Link from "next/link";
import { Bell, ChevronDown, ChevronRight, Home, Layers3, Radar, Search, Settings, ShoppingBag, Sparkles, Target, Truck, WandSparkles, Workflow } from "lucide-react";
import { usePathname } from "next/navigation";

import { ROUTES } from "@/config/routes";
import { LanguageToggle } from "@/design-system/components/LanguageToggle";
import { Language } from "@/lib/i18n";
import { cn } from "@/lib/utils";

type LayoutActivePath =
  | "dashboard"
  | "products"
  | "crawl"
  | "analyze"
  | "market"
  | "supplier"
  | "operation"
  | "admin"
  | "settings";

type DashboardLayoutProps = {
  children: ReactNode;
  rightRail?: ReactNode;
  lang: Language;
  activePath?: LayoutActivePath;
};

type TopNavKey =
  | "home"
  | "asset"
  | "capture"
  | "insight"
  | "market"
  | "supply"
  | "decision"
  | "growth"
  | "settings";

type TopNavItem = {
  key: TopNavKey;
  label: string;
  href: string;
  icon: typeof Home;
};

type SideNavItem = {
  label: string;
  hint: string;
  href: string;
};

const topNavItems: TopNavItem[] = [
  { key: "home", label: "首页", href: ROUTES.dashboard, icon: Home },
  { key: "asset", label: "商品资产", href: ROUTES.products, icon: ShoppingBag },
  { key: "capture", label: "数据采集", href: ROUTES.crawl, icon: Search },
  { key: "insight", label: "智能分析", href: ROUTES.analyze, icon: WandSparkles },
  { key: "market", label: "市场雷达", href: ROUTES.marketAnalysis, icon: Radar },
  { key: "supply", label: "供应网络", href: ROUTES.supplier, icon: Truck },
  { key: "decision", label: "AI决策", href: ROUTES.aiDiscovery, icon: Target },
  { key: "growth", label: "商业执行", href: ROUTES.operation, icon: Workflow },
  { key: "settings", label: "个人设置", href: ROUTES.settings, icon: Settings },
];

const sideNavMap: Record<Exclude<TopNavKey, "home">, { title: string; items: SideNavItem[] }> = {
  asset: {
    title: "商品资产",
    items: [
      { label: "商品列表", hint: "看全部商品", href: ROUTES.products },
      { label: "商品详情", hint: "进入单个商品详情", href: ROUTES.products },
      { label: "AI评分", hint: "看商品评分结果", href: ROUTES.products },
      { label: "利润分析", hint: "看利润空间", href: ROUTES.products },
      { label: "商品对比", hint: "做商品横向判断", href: ROUTES.products },
    ],
  },
  capture: {
    title: "数据采集",
    items: [
      { label: "URL采集", hint: "输入商品链接", href: ROUTES.crawl },
      { label: "采集任务", hint: "看采集运行情况", href: ROUTES.crawl },
      { label: "采集结果", hint: "查看采集结果", href: ROUTES.crawl },
    ],
  },
  insight: {
    title: "智能分析",
    items: [
      { label: "AI评分中心", hint: "看综合评分", href: ROUTES.analyze },
      { label: "商品分析", hint: "分析单个商品", href: ROUTES.analyze },
      { label: "类目分析", hint: "看类目表现", href: ROUTES.analyze },
      { label: "趋势预测", hint: "看趋势变化", href: ROUTES.analyze },
    ],
  },
  market: {
    title: "市场雷达",
    items: [
      { label: "热度地图", hint: "看市场热度", href: ROUTES.marketAnalysis },
      { label: "爆品榜单", hint: "看热门商品", href: ROUTES.marketAnalysis },
      { label: "类目趋势", hint: "看类目变化", href: ROUTES.marketAnalysis },
      { label: "风险预警", hint: "看风险提示", href: ROUTES.marketAnalysis },
    ],
  },
  supply: {
    title: "供应网络",
    items: [
      { label: "供应商列表", hint: "看可匹配供应商", href: ROUTES.supplier },
      { label: "价格对比", hint: "比不同平台价格", href: ROUTES.supplier },
      { label: "利润空间", hint: "看利润余量", href: ROUTES.supplier },
      { label: "推荐排序", hint: "看供应商优先级", href: ROUTES.supplier },
    ],
  },
  decision: {
    title: "AI决策",
    items: [
      { label: "推荐TOP10", hint: "看优先推荐商品", href: ROUTES.aiDiscovery },
      { label: "决策列表", hint: "看全部决策结果", href: ROUTES.dashboard },
      { label: "风险评分", hint: "看风险侧重点", href: ROUTES.dashboard },
      { label: "利润预测", hint: "看利润判断", href: ROUTES.dashboard },
    ],
  },
  growth: {
    title: "商业执行",
    items: [
      { label: "待执行", hint: "看待推进商品", href: ROUTES.operation },
      { label: "已执行", hint: "看已处理结果", href: ROUTES.operation },
      { label: "状态流转", hint: "看推进状态", href: ROUTES.operation },
    ],
  },
  settings: {
    title: "个人设置",
    items: [
      { label: "店铺绑定", hint: "管理店铺信息", href: ROUTES.settings },
      { label: "账号信息", hint: "查看当前账号", href: ROUTES.settings },
      { label: "密码修改", hint: "修改登录信息", href: ROUTES.settings },
    ],
  },
};

function getTopNavKey(pathname: string | null | undefined): TopNavKey {
  if (!pathname) return "home";
  if (pathname === "/dashboard" || pathname === "/") return "home";
  if (pathname.startsWith("/products") || pathname.startsWith("/product")) return "asset";
  if (pathname.startsWith("/crawl")) return "capture";
  if (pathname.startsWith("/analyze")) return "insight";
  if (pathname.startsWith("/market-analysis")) return "market";
  if (pathname.startsWith("/supplier")) return "supply";
  if (pathname.startsWith("/ai-discovery") || pathname.startsWith("/p5") || pathname.startsWith("/dashboard")) return "decision";
  if (pathname.startsWith("/operation")) return "growth";
  if (pathname.startsWith("/settings") || pathname.startsWith("/system/admin")) return "settings";
  return "home";
}

function shouldShowSideNav(topNavKey: TopNavKey) {
  return topNavKey !== "home";
}

export function NewDashboardLayout({ children, rightRail, lang }: DashboardLayoutProps) {
  const pathname = usePathname();
  const topNavKey = getTopNavKey(pathname);
  const showSideNav = shouldShowSideNav(topNavKey);
  const sideNav = topNavKey !== "home" ? sideNavMap[topNavKey] : null;

  return (
    <div className="min-h-screen bg-[#0B1220] text-white">
      <header className="fixed inset-x-0 top-0 z-40 h-16 border-b border-white/6 bg-[rgba(11,18,32,0.88)] backdrop-blur-xl">
        <div className="flex h-full items-center justify-between gap-6 px-4 md:px-6 xl:px-8">
          <div className="flex min-w-0 items-center gap-4">
            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-[linear-gradient(135deg,#4F7CFF,#6C5CE7)] shadow-[0_0_28px_rgba(79,124,255,0.24)]">
              <Sparkles className="h-5 w-5" />
            </div>
            <div className="min-w-0">
              <div className="truncate text-[17px] font-semibold leading-none text-white">AI跨境电商系统</div>
              <div className="mt-1 truncate text-xs text-white/45">AI Decision Platform</div>
            </div>
          </div>

          <nav className="hidden min-w-0 items-center gap-1 overflow-x-auto lg:flex">
            {topNavItems.map((item) => {
              const Icon = item.icon;
              const active = topNavKey === item.key;
              return (
                <Link
                  key={item.key}
                  href={item.href}
                  className={cn(
                    "flex min-w-[92px] items-center justify-center gap-2 rounded-full px-3 py-2 text-sm transition",
                    active ? "bg-[#4F7CFF]/14 text-[#4F7CFF]" : "text-white/45 hover:bg-white/[0.03] hover:text-white/80"
                  )}
                >
                  <Icon className="h-4 w-4" />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>

          <div className="flex items-center gap-3">
            <div className="hidden items-center gap-3 rounded-full border border-white/10 bg-[#111A2E] px-4 py-2 text-sm text-white/65 xl:flex">
              <Search className="h-4 w-4 text-white/35" />
              <span>搜索商品</span>
              <span className="text-white/25">|</span>
              <span>全站点</span>
              <ChevronDown className="h-4 w-4 text-white/35" />
            </div>

            <div className="hidden rounded-full border border-white/10 bg-white/[0.02] p-1.5 md:block">
              <LanguageToggle lang={lang} />
            </div>

            <button className="flex h-11 w-11 items-center justify-center rounded-full border border-white/10 bg-[#111A2E] text-white/70">
              <Bell className="h-4 w-4" />
            </button>
          </div>
        </div>
      </header>

      <div className="flex min-h-screen pt-16">
        {showSideNav && sideNav ? (
          <aside className="hidden w-[260px] shrink-0 border-r border-white/6 bg-[#0B1220] lg:block">
            <div className="h-full overflow-y-auto px-4 py-6">
              <div className="rounded-2xl border border-white/6 bg-[#111A2E] p-4">
                <div className="text-xs font-medium tracking-[0.18em] text-white/35">当前功能域</div>
                <div className="mt-3 flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-[#4F7CFF]/12 text-[#4F7CFF]">
                    <Layers3 className="h-4 w-4" />
                  </div>
                  <div>
                    <div className="text-base font-semibold text-white">{sideNav.title}</div>
                    <div className="text-xs text-white/40">页面内细分导航</div>
                  </div>
                </div>
              </div>

              <div className="mt-6 space-y-2">
                {sideNav.items.map((item) => {
                  const active = pathname === item.href || (item.href !== ROUTES.products && pathname?.startsWith(item.href));
                  return (
                    <Link
                      key={`${sideNav.title}-${item.label}`}
                      href={item.href}
                      className={cn(
                        "flex items-center justify-between rounded-2xl px-4 py-3 transition",
                        active ? "bg-[#111A2E] shadow-[inset_0_0_0_1px_rgba(255,255,255,0.08)]" : "hover:bg-white/[0.03]"
                      )}
                    >
                      <div className="min-w-0">
                        <div className={cn("truncate text-sm font-medium", active ? "text-white" : "text-white/72")}>{item.label}</div>
                        <div className="truncate text-xs text-white/38">{item.hint}</div>
                      </div>
                      <ChevronRight className={cn("h-4 w-4 shrink-0", active ? "text-white/65" : "text-white/18")} />
                    </Link>
                  );
                })}
              </div>
            </div>
          </aside>
        ) : null}

        <div className="min-w-0 flex-1 bg-[radial-gradient(circle_at_top,rgba(79,124,255,0.10),transparent_24%),linear-gradient(180deg,#0B1220,#0B1220)]">
          <div className="flex min-h-[calc(100vh-64px)] gap-6 px-4 py-6 md:px-6 xl:px-8">
            <main className="min-w-0 flex-1">{children}</main>
            {rightRail ? <aside className="hidden w-[360px] shrink-0 xl:block">{rightRail}</aside> : null}
          </div>
        </div>
      </div>
    </div>
  );
}
