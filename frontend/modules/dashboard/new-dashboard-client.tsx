"use client";

import Link from "next/link";
import { ArrowRight, BrainCircuit, PackageSearch, ScanSearch, Sparkles, TrendingUp, Truck, WandSparkles } from "lucide-react";

import { useKpiRealtime } from "@/components/dashboard/realtime/use-kpi-realtime";
import { Card } from "@/design-system/components";
import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { ROUTES, productDetailRoute } from "@/config/routes";
import type { DashboardSourcesResponse, DashboardSummaryResponse, DashboardTasksResponse, DashboardTrendsResponse, ProductListResponse } from "@/lib/types";
import { Language, t } from "@/lib/i18n";

export function NewDashboardClient({
  token,
  lang,
  initialSummary,
  initialTrends,
  initialTasks,
  initialSources,
  productList,
}: {
  token: string;
  lang: Language;
  initialSummary: DashboardSummaryResponse;
  initialTrends: DashboardTrendsResponse;
  initialTasks: DashboardTasksResponse;
  initialSources: DashboardSourcesResponse;
  productList: ProductListResponse;
}) {
  const text = t(lang);
  const sourceCountCard = {
    key: "sources",
    label: text.sourceOverviewTitle,
    value: initialSources.sources.length,
    delta_text: `${text.sourceHealthOk} ${initialSources.sources.filter((item) => item.health === "ok").length} ${text.productsUnit}`,
    trend: "up" as const,
  };
  const kpi = useKpiRealtime(token, initialSummary, sourceCountCard);
  const summary = kpi.summary;
  const statCards = kpi.cards.slice(0, 4);
  const topProducts = summary.latest_products.slice(0, 5);
  const recommendedProducts = productList.items.slice(0, 3);
  const trendPoints = initialTrends.series.points.slice(-4);
  const trendGrowth = trendPoints.length > 1 ? trendPoints[trendPoints.length - 1].product_count - trendPoints[0].product_count : 0;

  return (
    <XBorderLayout lang={lang} activePath="dashboard">
      <div className="space-y-6">
        <Card className="rounded-[32px] border border-white/8 bg-[linear-gradient(135deg,rgba(17,24,39,0.92),rgba(15,23,42,0.84))] p-7 shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <div className="flex flex-col gap-6 xl:flex-row xl:items-end xl:justify-between">
            <div>
              <div className="inline-flex items-center gap-2 rounded-full border border-[#60a5fa]/20 bg-[#60a5fa]/10 px-4 py-2 text-sm text-[#7dd3fc]">
                <Sparkles className="h-4 w-4" />
                {text.dashboardHeroBadge}
              </div>
              <h1 className="mt-5 text-4xl font-semibold tracking-tight text-white">{text.dashboardHeroTitle}</h1>
              <p className="mt-3 max-w-3xl text-sm leading-7 text-white/60">
                {text.dashboardHeroDesc}
              </p>
            </div>
            <div className="flex flex-wrap gap-3">
              <QuickEntry href={ROUTES.crawl} icon={<ScanSearch className="h-4 w-4" />} label={text.dashboardQuickCrawl} />
              <QuickEntry href={ROUTES.analyze} icon={<BrainCircuit className="h-4 w-4" />} label={text.dashboardQuickAnalyze} />
              <QuickEntry href={ROUTES.products} icon={<PackageSearch className="h-4 w-4" />} label={text.dashboardQuickProducts} />
              <QuickEntry href={ROUTES.aiDiscovery} icon={<WandSparkles className="h-4 w-4" />} label={text.navDiscovery} />
              <QuickEntry href={ROUTES.supplier} icon={<Truck className="h-4 w-4" />} label={text.navSupplier} />
              <QuickEntry href={ROUTES.operation} icon={<Sparkles className="h-4 w-4" />} label={text.navOperation} />
            </div>
          </div>
        </Card>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
          {statCards.map((card) => (
            <Card key={card.key} className="rounded-[24px] border border-white/8 bg-[#121c2c] p-5 shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
              <div className="text-sm text-white/50">{card.label}</div>
              <div className="mt-3 text-[34px] font-semibold leading-none text-white">{card.value}</div>
              <div className={`mt-4 text-sm ${card.trend === "up" ? "text-emerald-300" : card.trend === "down" ? "text-rose-300" : "text-white/45"}`}>
                {card.delta_text || text.dashboardNoDelta}
              </div>
            </Card>
          ))}
        </div>

        <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
          <Card className="rounded-[28px] border border-white/8 bg-[#121c2c] p-6 shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <div className="mb-5 flex items-center justify-between">
              <div>
                <div className="text-xl font-semibold text-white">{text.dashboardTodayRecommended}</div>
                <div className="mt-1 text-sm text-white/45">{text.dashboardTodayRecommendedDesc}</div>
              </div>
              <Link href={ROUTES.products} className="text-sm text-[#60a5fa]">{text.dashboardViewAll}</Link>
            </div>
            <div className="space-y-4">
              {recommendedProducts.length ? (
                recommendedProducts.map((product) => (
                  <div key={product.id} className="flex flex-col gap-4 rounded-[24px] border border-white/8 bg-white/[0.03] p-4 md:flex-row md:items-center md:justify-between">
                    <div className="flex items-center gap-4">
                      {product.images?.[0]?.image_url ? (
                        <img src={product.images[0].image_url} alt={product.title} className="h-20 w-20 rounded-2xl border border-white/10 object-cover" />
                      ) : (
                        <div className="h-20 w-20 rounded-2xl border border-white/10 bg-white/[0.04]" />
                      )}
                      <div>
                        <div className="text-base font-medium text-white">{product.title}</div>
                        <div className="mt-1 text-sm text-white/45">{product.title_zh || text.noTranslation}</div>
                        <div className="mt-2 text-sm text-white/60">
                          {text.price}：{product.current_price ?? "—"}　{text.rating}：{product.rating ?? "—"}　{text.reviews}：{product.review_count ?? 0}
                        </div>
                      </div>
                    </div>
                    <Link href={productDetailRoute(product.id)} className="inline-flex items-center gap-2 rounded-full border border-[#60a5fa]/20 bg-[#60a5fa]/10 px-4 py-2 text-sm text-[#7dd3fc]">
                      {text.dashboardViewDetail}
                      <ArrowRight className="h-4 w-4" />
                    </Link>
                  </div>
                ))
              ) : (
                <div className="rounded-[24px] border border-dashed border-white/10 bg-white/[0.02] px-5 py-12 text-center text-sm text-white/35">
                  {text.dashboardNoRecommended}
                </div>
              )}
            </div>
          </Card>

          <Card className="rounded-[28px] border border-white/8 bg-[#121c2c] p-6 shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <div className="text-xl font-semibold text-white">{text.dashboardTrendTitle}</div>
            <div className="mt-1 text-sm text-white/45">{text.dashboardTrendDesc}</div>

            <div className="mt-6 rounded-[24px] border border-white/8 bg-[linear-gradient(180deg,rgba(37,99,235,0.16),rgba(109,40,217,0.06))] p-5">
              <div className="flex items-center gap-2 text-sm text-[#93c5fd]">
                <TrendingUp className="h-4 w-4" />
                {text.dashboardTrendSummary}
              </div>
              <div className="mt-4 text-[32px] font-semibold text-white">{trendPoints.at(-1)?.date || text.dashboardTrendPending}</div>
              <div className="mt-2 text-sm text-white/60">
                {trendPoints.length
                  ? `${text.dashboardTrendGrowth} ${trendGrowth >= 0 ? "+" : ""}${trendGrowth}`
                  : text.dashboardTrendNeedData}
              </div>
            </div>

            <div className="mt-5 grid gap-3">
              <OpportunityMiniCard label={text.dashboardTrendWindow} value={initialTrends.series.period} />
              <OpportunityMiniCard label={text.dashboardTrendTopCategory} value={summary.top_categories[0]?.name || text.dashboardUncategorized} />
              <OpportunityMiniCard label={text.dashboardTrendActiveSource} value={String(initialSources.sources.filter((item) => item.health === "ok").length)} />
            </div>
          </Card>
        </div>

        <div>
          <Card className="rounded-[28px] border border-white/8 bg-[#121c2c] p-6 shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <div className="mb-5 flex items-center justify-between">
              <div>
                <div className="text-xl font-semibold text-white">{text.dashboardTopListTitle}</div>
                <div className="mt-1 text-sm text-white/45">{text.dashboardTopListDesc}</div>
              </div>
              <Link href={ROUTES.products} className="text-sm text-[#60a5fa]">{text.dashboardQuickProducts}</Link>
            </div>
            <div className="space-y-3">
              {topProducts.length ? (
                topProducts.map((product, index) => (
                  <div key={product.id} className="flex items-center justify-between rounded-[22px] border border-white/8 bg-white/[0.03] px-4 py-4">
                    <div className="min-w-0">
                      <div className="flex items-center gap-3">
                        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[#1d4ed8]/20 text-sm font-semibold text-[#93c5fd]">
                          {index + 1}
                        </div>
                        <div className="truncate text-[15px] font-medium text-white">{product.title}</div>
                      </div>
                      <div className="mt-2 pl-11 text-sm text-white/45">{product.platform_name} · {product.category_name || text.dashboardUncategorized} · {product.price}</div>
                    </div>
                    <Link href={productDetailRoute(product.id)} className="text-sm text-[#60a5fa]">{text.viewDetail}</Link>
                  </div>
                ))
              ) : (
                <div className="rounded-[24px] border border-dashed border-white/10 bg-white/[0.02] px-5 py-10 text-center text-sm text-white/35">
                  {text.dashboardNoTopList}
                </div>
              )}
            </div>
          </Card>
        </div>
      </div>
    </XBorderLayout>
  );
}

function QuickEntry({
  href,
  icon,
  label,
}: {
  href: string;
  icon: React.ReactNode;
  label: string;
}) {
  return (
    <Link
      href={href}
      className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.03] px-5 py-3 text-sm text-white/75 transition hover:border-white/20 hover:bg-white/[0.06] hover:text-white"
    >
      {icon}
      {label}
    </Link>
  );
}

function OpportunityMiniCard({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-[22px] border border-white/8 bg-white/[0.03] px-4 py-4">
      <div className="text-sm text-white/45">{label}</div>
      <div className="mt-2 text-xl font-semibold text-white">{value}</div>
    </div>
  );
}
