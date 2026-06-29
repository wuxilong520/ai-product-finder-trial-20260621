"use client";

import type { ReactNode } from "react";
import Link from "next/link";
import { Bell, ChevronDown, ChevronRight, Home, LineChart, Search, Settings, ShoppingBag, Sparkles, WalletCards } from "lucide-react";
import { usePathname } from "next/navigation";

import { ROUTES } from "@/config/routes";
import { LanguageToggle } from "@/design-system/components/LanguageToggle";
import { Language } from "@/lib/i18n";
import { cn } from "@/lib/utils";

type LayoutActivePath = "home" | "products" | "insights" | "action" | "settings";

type DashboardLayoutProps = {
  children: ReactNode;
  rightRail?: ReactNode;
  lang: Language;
  activePath?: LayoutActivePath;
};

type TopNavKey = LayoutActivePath;

function getLayoutText(lang: Language) {
  if (lang === "en") {
    return {
      topNavItems: [
        { key: "home", label: "Home", href: ROUTES.home, icon: Home },
        { key: "products", label: "Products", href: ROUTES.products, icon: ShoppingBag },
        { key: "insights", label: "Insights", href: ROUTES.insights, icon: LineChart },
        { key: "action", label: "Action Center", href: ROUTES.actionCenter, icon: WalletCards },
        { key: "settings", label: "Account", href: ROUTES.settings, icon: Settings },
      ] as const,
      sideNavMap: {
        products: {
          title: "Products",
          items: [
            { label: "Product List", hint: "Browse all products", href: ROUTES.products },
            { label: "Product Detail", hint: "Review one product", href: ROUTES.products },
            { label: "Product Compare", hint: "Compare side by side", href: ROUTES.products },
          ],
        },
        insights: {
          title: "Insights",
          items: [
            { label: "Market Trends", hint: "See trend changes", href: ROUTES.insights },
            { label: "Hot Categories", hint: "See growing categories", href: ROUTES.insights },
            { label: "Best Sellers", hint: "See hot directions", href: ROUTES.insights },
            { label: "Risk Alerts", hint: "See possible risks", href: ROUTES.insights },
            { label: "Future Outlook", hint: "See future signals", href: ROUTES.insights },
          ],
        },
        action: {
          title: "Action Center",
          items: [
            { label: "Top 10 Picks", hint: "See priority picks", href: ROUTES.actionCenter },
            { label: "Profit Review", hint: "Check margin room", href: ROUTES.actionCenter },
            { label: "Supplier Picks", hint: "Review source options", href: ROUTES.actionCenter },
            { label: "Price Compare", hint: "Compare price ranges", href: ROUTES.actionCenter },
            { label: "Launch Queue", hint: "Track execution status", href: ROUTES.actionCenter },
          ],
        },
        settings: {
          title: "Account",
          items: [
            { label: "Store Links", hint: "Manage store info", href: ROUTES.settings },
            { label: "Profile", hint: "View account details", href: ROUTES.settings },
            { label: "Password", hint: "Change login password", href: ROUTES.settings },
          ],
        },
      } as Record<Exclude<TopNavKey, "home">, { title: string; items: Array<{ label: string; hint: string; href: string }> }>,
      productName: "AI Commerce Platform",
      productDesc: "AI Business Decision Platform",
      searchPlaceholder: "Search products",
      allSites: "All sites",
      currentModule: "Current module",
      sideGuide: "Page navigation",
    };
  }

  return {
    topNavItems: [
      { key: "home", label: "首页", href: ROUTES.home, icon: Home },
      { key: "products", label: "商品库", href: ROUTES.products, icon: ShoppingBag },
      { key: "insights", label: "市场洞察", href: ROUTES.insights, icon: LineChart },
      { key: "action", label: "商业执行", href: ROUTES.actionCenter, icon: WalletCards },
      { key: "settings", label: "账户", href: ROUTES.settings, icon: Settings },
    ] as const,
    sideNavMap: {
      products: {
        title: "商品库",
        items: [
          { label: "商品列表", hint: "查看全部商品", href: ROUTES.products },
          { label: "商品详情", hint: "查看单个商品表现", href: ROUTES.products },
          { label: "商品对比", hint: "做横向比较", href: ROUTES.products },
        ],
      },
      insights: {
        title: "市场洞察",
        items: [
          { label: "市场趋势", hint: "看趋势变化", href: ROUTES.insights },
          { label: "热门类目", hint: "看增长类目", href: ROUTES.insights },
          { label: "爆款榜单", hint: "看热销方向", href: ROUTES.insights },
          { label: "风险提示", hint: "看潜在风险", href: ROUTES.insights },
          { label: "未来趋势预测", hint: "看未来判断", href: ROUTES.insights },
        ],
      },
      action: {
        title: "商业执行",
        items: [
          { label: "推荐商品TOP10", hint: "查看优先推荐", href: ROUTES.actionCenter },
          { label: "利润分析", hint: "查看利润空间", href: ROUTES.actionCenter },
          { label: "供应商推荐", hint: "查看可合作货源", href: ROUTES.actionCenter },
          { label: "价格对比", hint: "比较价格区间", href: ROUTES.actionCenter },
          { label: "上架执行队列", hint: "查看执行状态", href: ROUTES.actionCenter },
        ],
      },
      settings: {
        title: "账户",
        items: [
          { label: "店铺绑定", hint: "管理店铺资料", href: ROUTES.settings },
          { label: "账号信息", hint: "查看账号信息", href: ROUTES.settings },
          { label: "密码修改", hint: "修改登录密码", href: ROUTES.settings },
        ],
      },
    } as Record<Exclude<TopNavKey, "home">, { title: string; items: Array<{ label: string; hint: string; href: string }> }>,
    productName: "AI跨境电商系统",
    productDesc: "AI Business Decision Platform",
    searchPlaceholder: "搜索商品",
    allSites: "全部站点",
    currentModule: "当前模块",
    sideGuide: "页面内功能导航",
  };
}

function getTopNavKey(pathname: string | null | undefined): TopNavKey {
  if (!pathname || pathname === "/") return "home";
  if (pathname.startsWith("/products")) return "products";
  if (pathname.startsWith("/insights")) return "insights";
  if (pathname.startsWith("/action-center")) return "action";
  if (pathname.startsWith("/settings")) return "settings";
  return "home";
}

export function NewDashboardLayout({ children, rightRail, lang }: DashboardLayoutProps) {
  const pathname = usePathname();
  const topNavKey = getTopNavKey(pathname);
  const showSideNav = topNavKey !== "home";
  const layoutText = getLayoutText(lang);
  const topNavItems = layoutText.topNavItems;
  const sideNavMap = layoutText.sideNavMap;
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
              <div className="truncate text-[17px] font-semibold leading-none text-white">{layoutText.productName}</div>
              <div className="mt-1 truncate text-xs text-white/45">{layoutText.productDesc}</div>
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
              <span>{layoutText.searchPlaceholder}</span>
              <span className="text-white/25">|</span>
              <span>{layoutText.allSites}</span>
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
                <div className="text-xs font-medium tracking-[0.18em] text-white/35">{layoutText.currentModule}</div>
                <div className="mt-3 text-base font-semibold text-white">{sideNav.title}</div>
                <div className="mt-1 text-xs text-white/40">{layoutText.sideGuide}</div>
              </div>

              <div className="mt-6 space-y-2">
                {sideNav.items.map((item) => {
                  const active = pathname === item.href || pathname?.startsWith(`${item.href}/`);
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
