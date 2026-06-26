"use client";

import Link from "next/link";
import { BarChart3, BrainCircuit, CircleDollarSign, FileBarChart2, PackageSearch, Radar, ScanSearch, ShieldAlert, ShoppingBag, Sparkles, Truck } from "lucide-react";

import { ROUTES, productDetailRoute } from "@/config/routes";
import { DashboardSection, DashboardMetricCard, LineChartPanel, BarChartPanel, DonutChartPanel, HeatmapPanel } from "@/components/dashboard/bi-primitives";
import { TaskPanel } from "@/components/dashboard/task-panel";
import { Badge, Button } from "@/design-system/components";
import { Language, t } from "@/lib/i18n";
import type {
  DashboardSourcesResponse,
  DashboardSummaryResponse,
  DashboardTasksResponse,
  DashboardTrendsResponse,
  P5RankingsResponse,
  P5RecommendationsResponse,
  ProductListResponse,
} from "@/lib/types";

function shortDate(date: string) {
  return date.slice(5);
}

function currencyValue(value: number) {
  return `¥${value.toLocaleString(undefined, { maximumFractionDigits: 0 })}`;
}

export function DashboardCommandCenter({
  token,
  lang,
  summary,
  trends,
  tasks,
  sources,
  products,
  rankings,
  recommendations,
  isAdmin,
}: {
  token: string;
  lang: Language;
  summary: DashboardSummaryResponse;
  trends: DashboardTrendsResponse;
  tasks: DashboardTasksResponse;
  sources: DashboardSourcesResponse;
  products: ProductListResponse;
  rankings: P5RankingsResponse | null;
  recommendations: P5RecommendationsResponse | null;
  isAdmin: boolean;
}) {
  const text = t(lang);
  const trendValues = trends.series.points.map((item) => item.product_count);
  const trendLabels = trends.series.points.map((item) => shortDate(item.date));
  const latestProducts = products.items.slice(0, 6);
  const topRecommendations = recommendations?.items.slice(0, 5) || [];
  const sourceItems = sources.sources.slice(0, 5);
  const categoryBars = summary.top_categories.slice(0, 5).map((item) => ({
    label: item.name,
    value: item.product_count,
    note: `${item.product_count} ${text.productsUnit}`,
  }));
  const riskItems = [
    { label: "失败任务", value: tasks.recent_runs.filter((item) => item.status === "failed" || item.status === "error").length, color: "#fb7185" },
    { label: "阻塞任务", value: tasks.recent_runs.filter((item) => item.status === "blocked").length, color: "#fbbf24" },
    { label: "活跃数据源", value: sources.sources.filter((item) => item.health === "ok").length, color: "#34d399" },
    { label: "分析结果", value: Number(summary.cards.find((item) => item.key === "analyses")?.value || 0), color: "#60a5fa" },
  ];
  const heatmapItems = (rankings?.profit_ranking.top_10 || []).slice(0, 6).map((item) => ({
    label: item.title.slice(0, 8),
    score: Math.round(item.score),
  }));
  const salesMetric = Number(summary.cards.find((item) => item.key === "products")?.value || sources.storage.total_products || 0);
  const analyzeMetric = Number(summary.cards.find((item) => item.key === "analyses")?.value || 0);
  const aiIndex = topRecommendations.length
    ? Math.round(topRecommendations.reduce((sum, item) => sum + item.recommendation_score, 0) / topRecommendations.length)
    : 0;
  const profitMetric = topRecommendations.reduce((sum, item) => sum + item.estimated_profit, 0);
  const marketMetric = summary.top_categories.reduce((sum, item) => sum + item.product_count, 0);

  return (
    <div className="space-y-6">
      <section className="rounded-[20px] border border-white/8 bg-[linear-gradient(135deg,rgba(18,28,44,0.98),rgba(10,17,29,0.98))] p-6 shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
        <div className="flex flex-col gap-5 xl:flex-row xl:items-end xl:justify-between">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-[#60a5fa]/20 bg-[#60a5fa]/10 px-4 py-2 text-sm text-[#93c5fd]">
              <Sparkles className="h-4 w-4" />
              BI 决策驾驶舱
            </div>
            <h1 className="mt-4 text-4xl font-semibold tracking-tight text-white">AI跨境电商决策驾驶舱</h1>
            <p className="mt-3 max-w-4xl text-sm leading-7 text-white/55">
              首页只保留真正能帮助你做判断的数据：商品规模、推荐利润、市场热度、风险状态，以及所有核心业务入口。
            </p>
          </div>
          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <QuickEntry href={ROUTES.products} icon={<PackageSearch className="h-4 w-4" />} label="商品中心" />
            <QuickEntry href={ROUTES.aiDiscovery} icon={<BrainCircuit className="h-4 w-4" />} label="AI选品中心" />
            <QuickEntry href={ROUTES.supplier} icon={<Truck className="h-4 w-4" />} label="供应链中心" />
            <QuickEntry href={ROUTES.operation} icon={<ShoppingBag className="h-4 w-4" />} label="运营中心" />
          </div>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <DashboardMetricCard
          label="总销量（以商品规模代理）"
          value={salesMetric.toLocaleString()}
          hint="当前系统没有真实销售额接口，这里展示真实商品总数"
          tone="blue"
          sparkline={trendValues}
        />
        <DashboardMetricCard
          label="总利润"
          value={currencyValue(profitMetric)}
          hint="来自 P5 推荐列表的真实预估利润累计"
          tone="green"
          sparkline={topRecommendations.map((item) => Math.max(Math.round(item.estimated_profit), 0))}
        />
        <DashboardMetricCard
          label="市场热度"
          value={marketMetric.toLocaleString()}
          hint="来自真实类目分布总量"
          tone="orange"
          sparkline={summary.top_categories.map((item) => item.product_count)}
        />
        <DashboardMetricCard
          label="AI推荐指数"
          value={`${aiIndex} / 100`}
          hint="来自 P5 推荐商品平均推荐分"
          tone="violet"
          sparkline={topRecommendations.map((item) => Math.round(item.recommendation_score))}
        />
      </section>

      <section className="grid gap-6 xl:grid-cols-2">
        <DashboardSection title="销售趋势图" subtitle="使用真实商品增长趋势作为当前业务规模趋势">
          <LineChartPanel values={trendValues.length ? trendValues : [0, 0, 0, 0, 0, 0, 0]} labels={trendLabels.length ? trendLabels : ["--", "--", "--", "--", "--", "--", "--"]} tone="blue" />
        </DashboardSection>
        <DashboardSection title="市场热度图" subtitle="按真实类目数量看当前市场分布">
          <BarChartPanel items={categoryBars.length ? categoryBars : [{ label: "暂无数据", value: 0 }]} tone="orange" />
        </DashboardSection>
        <DashboardSection title="利润结构图" subtitle="基于 P5 推荐商品的预估利润结构">
          <DonutChartPanel
            items={
              topRecommendations.length
                ? topRecommendations.slice(0, 4).map((item, index) => ({
                    label: item.title_zh || item.title.slice(0, 16),
                    value: Math.max(Math.round(item.estimated_profit), 1),
                    color: ["#60a5fa", "#34d399", "#fbbf24", "#a78bfa"][index] || "#60a5fa",
                  }))
                : [{ label: "暂无利润数据", value: 1, color: "#334155" }]
            }
          />
        </DashboardSection>
        <DashboardSection title="风险分析图" subtitle="根据失败任务、阻塞任务和活跃数据源看当前风险">
          <BarChartPanel items={riskItems.map((item) => ({ label: item.label, value: item.value }))} tone="red" />
        </DashboardSection>
      </section>

      <section className="grid gap-6 xl:grid-cols-3">
        <DashboardSection title="商品库预览" subtitle="最近进入系统的真实商品">
          <div className="space-y-3">
            {latestProducts.length ? latestProducts.map((product) => (
              <Link key={product.id} href={productDetailRoute(product.id)} className="flex items-center gap-3 rounded-[16px] border border-white/8 bg-white/[0.03] p-3 transition hover:bg-white/[0.06]">
                {product.images?.[0]?.image_url ? (
                  <img src={product.images[0].image_url} alt={product.title} className="h-14 w-14 rounded-2xl border border-white/8 object-cover" />
                ) : (
                  <div className="h-14 w-14 rounded-2xl border border-white/8 bg-white/[0.04]" />
                )}
                <div className="min-w-0 flex-1">
                  <div className="truncate text-sm font-medium text-white">{product.title}</div>
                  <div className="mt-1 text-xs text-white/45">{product.title_zh || text.noTranslation}</div>
                </div>
                <div className="text-right text-xs text-white/50">
                  <div>{product.current_price ?? "—"}</div>
                  <div>{product.review_count ?? 0}评</div>
                </div>
              </Link>
            )) : <EmptyBlock text="当前还没有真实商品数据" />}
          </div>
        </DashboardSection>

        <DashboardSection title="AI选品推荐 TOP10" subtitle="来自 P5 全局推荐，不是静态假数据">
          <div className="space-y-3">
            {topRecommendations.length ? topRecommendations.map((item, index) => (
              <Link key={`${item.product_id}-${index}`} href={productDetailRoute(item.product_id)} className="flex items-center justify-between rounded-[16px] border border-white/8 bg-white/[0.03] px-4 py-3 transition hover:bg-white/[0.06]">
                <div className="min-w-0">
                  <div className="truncate text-sm font-medium text-white">TOP {index + 1} · {item.title_zh || item.title}</div>
                  <div className="mt-1 text-xs text-white/45">{item.keyword}</div>
                </div>
                <Badge variant={item.recommendation_score >= 80 ? "success" : item.recommendation_score >= 60 ? "warning" : "neutral"} className="px-3 py-1.5 text-sm">
                  {Math.round(item.recommendation_score)}
                </Badge>
              </Link>
            )) : <EmptyBlock text="当前还没有 P5 推荐结果" />}
          </div>
        </DashboardSection>

        <DashboardSection title="供应链状态" subtitle="展示真实供应链模块的当前入口状态">
          <div className="space-y-3">
            {sourceItems.length ? sourceItems.map((item) => (
              <div key={item.platform_code} className="rounded-[16px] border border-white/8 bg-white/[0.03] px-4 py-3">
                <div className="flex items-center justify-between">
                  <div className="text-sm font-medium text-white">{item.platform_name}</div>
                  <div className={item.health === "ok" ? "text-sm text-emerald-300" : item.health === "warning" ? "text-sm text-amber-300" : "text-sm text-rose-300"}>
                    {item.health}
                  </div>
                </div>
                <div className="mt-2 text-xs text-white/45">{item.product_count} {text.productsUnit} · {item.last_activity_text}</div>
              </div>
            )) : <EmptyBlock text="当前还没有数据源状态" />}
          </div>
        </DashboardSection>

        <DashboardSection title="任务中心" subtitle="最近任务状态和实时更新能力" className="xl:col-span-2">
          <TaskPanel token={token} initialTasks={tasks} initialSources={sources} lang={lang} />
        </DashboardSection>

        <DashboardSection title="市场分析" subtitle="热门类目和机会强度热力视图">
          <HeatmapPanel values={heatmapItems.length ? heatmapItems : [{ label: "暂无", score: 0 }]} />
        </DashboardSection>

        <DashboardSection title="决策中心" subtitle="从商品情报、市场和供应链整合出的全局排行">
          <div className="space-y-3">
            {(rankings?.growth_ranking.top_10 || []).slice(0, 5).map((item, index) => (
              <Link key={`decision-${item.product_id}-${index}`} href={productDetailRoute(item.product_id)} className="flex items-center justify-between rounded-[16px] border border-white/8 bg-white/[0.03] px-4 py-3 transition hover:bg-white/[0.06]">
                <div>
                  <div className="text-sm font-medium text-white">TOP {index + 1} · {item.title}</div>
                  <div className="mt-1 text-xs text-white/45">{item.category || text.dashboardUncategorized}</div>
                </div>
                <Badge variant="brand" className="px-3 py-1.5 text-sm">{Math.round(item.score)}</Badge>
              </Link>
            ))}
            {!rankings?.growth_ranking.top_10.length ? <EmptyBlock text="当前还没有决策排行数据" /> : null}
          </div>
        </DashboardSection>

        <DashboardSection title="运营中心" subtitle="从推荐池进入运营动作的准备区">
          <div className="space-y-3">
            {topRecommendations.slice(0, 3).map((item) => (
              <div key={`op-${item.product_id}`} className="rounded-[16px] border border-white/8 bg-white/[0.03] p-4">
                <div className="text-sm font-medium text-white">{item.title_zh || item.title}</div>
                <div className="mt-2 flex flex-wrap gap-2">
                  <Badge variant="neutral" className="px-3 py-1.5 text-xs">待选</Badge>
                  <Badge variant="warning" className="px-3 py-1.5 text-xs">已选</Badge>
                  <Badge variant="success" className="px-3 py-1.5 text-xs">已上架</Badge>
                </div>
                <div className="mt-3">
                  <Button asChild className="w-full">
                    <Link href={ROUTES.operation}>进入执行中心</Link>
                  </Button>
                </div>
              </div>
            ))}
            {!topRecommendations.length ? <EmptyBlock text="当前还没有可进入运营流程的推荐商品" /> : null}
          </div>
        </DashboardSection>

        <DashboardSection title="数据报表" subtitle="用真实排行和类目结果做 BI 汇总">
          <div className="grid gap-3 sm:grid-cols-2">
            <SimpleMetric icon={<FileBarChart2 className="h-4 w-4" />} label="扫描商品数" value={String(rankings?.scanned_products || 0)} />
            <SimpleMetric icon={<CircleDollarSign className="h-4 w-4" />} label="推荐利润池" value={currencyValue(profitMetric)} />
            <SimpleMetric icon={<Radar className="h-4 w-4" />} label="推荐商品数" value={String(topRecommendations.length)} />
            <SimpleMetric icon={<BarChart3 className="h-4 w-4" />} label="类目数量" value={String(summary.top_categories.length)} />
          </div>
        </DashboardSection>

        {isAdmin ? (
          <DashboardSection title="系统状态" subtitle="管理员可见，普通用户不展示">
            <div className="space-y-3">
              <div className="rounded-[16px] border border-white/8 bg-white/[0.03] px-4 py-3 text-sm text-white/70">
                该模块已隐藏到系统管理页，避免首页暴露技术信息。
              </div>
              <Button asChild variant="outline" className="w-full">
                <Link href={ROUTES.systemAdmin}>进入系统管理</Link>
              </Button>
            </div>
          </DashboardSection>
        ) : null}
      </section>
    </div>
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
    <Link href={href} className="inline-flex items-center justify-center gap-2 rounded-[16px] border border-white/10 bg-white/[0.03] px-4 py-3 text-sm text-white/80 transition hover:bg-white/[0.06] hover:text-white">
      {icon}
      {label}
    </Link>
  );
}

function SimpleMetric({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-[16px] border border-white/8 bg-white/[0.03] px-4 py-4">
      <div className="flex items-center gap-2 text-sm text-white/55">
        {icon}
        {label}
      </div>
      <div className="mt-3 text-xl font-semibold text-white">{value}</div>
    </div>
  );
}

function EmptyBlock({ text }: { text: string }) {
  return <div className="rounded-[16px] border border-dashed border-white/10 bg-white/[0.02] px-4 py-8 text-center text-sm text-white/40">{text}</div>;
}
