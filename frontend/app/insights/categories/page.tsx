import Link from "next/link";

import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { Card, CardContent, CardHeader, CardTitle, EmptyState } from "@/design-system/components";
import { ROUTES } from "@/config/routes";
import { getDashboardSummary, getDashboardTrends } from "@/lib/api-gateway";
import { EMPTY_DASHBOARD_SUMMARY, EMPTY_DASHBOARD_TRENDS, safeLoad } from "@/lib/dashboard-fallback";
import { loadFlowPageData } from "@/lib/flow-page-data";

export default async function InsightsCategoriesPage() {
  const { lang, token, tasks } = await loadFlowPageData();
  const [summary, trends] = await Promise.all([
    safeLoad(() => getDashboardSummary(token), EMPTY_DASHBOARD_SUMMARY),
    safeLoad(() => getDashboardTrends(token), EMPTY_DASHBOARD_TRENDS),
  ]);

  const topCategories = summary.top_categories.slice(0, 8);
  const latestProducts = summary.latest_products.slice(0, 6);
  const latestTrendPoint = trends.series.points[trends.series.points.length - 1];
  const firstTrendPoint = trends.series.points[0];
  const trendDelta = latestTrendPoint && firstTrendPoint
    ? latestTrendPoint.product_count - firstTrendPoint.product_count
    : 0;

  return (
    <XBorderLayout lang={lang} activePath="insights">
      <div className="space-y-6">
        <Card className="border-white/8 bg-[#111A2E] p-6 shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <div className="flex flex-col gap-5 xl:flex-row xl:items-end xl:justify-between">
            <div className="max-w-3xl">
              <div className="text-xs uppercase tracking-[0.24em] text-white/40">商航AI · 类目市场页</div>
              <h1 className="mt-2 text-3xl font-semibold tracking-tight text-white">先看类目，再决定做哪个具体商品</h1>
              <p className="mt-3 text-sm leading-7 text-white/60">
                这是商航AI主流程的第一步。你先看当前系统里已经形成结果的类目分布、最近趋势和最新进入系统的商品，再决定下一步要不要继续做单品判断。
              </p>
            </div>
            <div className="grid gap-3 md:grid-cols-3 xl:min-w-[520px]">
              <MetricTile label="当前类目数" value={`${topCategories.length} 个`} />
              <MetricTile label="最近任务状态数" value={`${tasks.states.length} 条`} />
              <MetricTile label="趋势变化" value={trendDelta > 0 ? `+${trendDelta}` : `${trendDelta}`} />
            </div>
          </div>
        </Card>

        <Card className="border-white/8 bg-[#111A2E] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <CardHeader>
            <CardTitle>现在值得优先关注的类目</CardTitle>
          </CardHeader>
          <CardContent>
            {topCategories.length ? (
              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                {topCategories.map((item, index) => (
                  <div key={`${item.name}-${index}`} className="rounded-2xl border border-white/8 bg-white/5 p-4">
                    <div className="flex items-center justify-between gap-3">
                      <div className="text-sm font-medium text-white">TOP {index + 1}</div>
                      <div className="text-xs text-[#9CC0FF]">类目</div>
                    </div>
                    <div className="mt-4 text-lg font-semibold text-white">{item.name}</div>
                    <div className="mt-2 text-sm text-white/60">当前入库商品数：{item.product_count}</div>
                    <div className="mt-4 h-2 rounded-full bg-white/8">
                      <div
                        className="h-2 rounded-full bg-[linear-gradient(90deg,#4F7CFF,#3DD68C)]"
                        style={{ width: `${Math.min(100, item.product_count * 8)}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState text="当前还没有足够的类目结果。你可以先发起一轮商品判断任务，让系统逐步沉淀类目数据。" />
            )}
          </CardContent>
        </Card>

        <div className="grid gap-6 xl:grid-cols-2">
          <Card className="border-white/8 bg-[#111A2E] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <CardTitle>最近趋势变化</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <InfoLine label="趋势周期" value={trends.series.period || "—"} />
              <InfoLine label="趋势点数" value={`${trends.series.points.length} 个`} />
              <InfoLine label="峰值" value={`${trends.series.peak_value || 0}`} />
              <InfoLine
                label="最新点"
                value={latestTrendPoint ? `${latestTrendPoint.date} / ${latestTrendPoint.product_count}` : "暂无"}
              />
              <div className="rounded-2xl border border-white/8 bg-white/5 p-4 text-sm leading-7 text-white/68">
                这里显示的是系统现在已经沉淀下来的趋势结果，不是假装已经拿到了全网所有类目的实时市场大盘。
              </div>
            </CardContent>
          </Card>

          <Card className="border-white/8 bg-[#111A2E] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <CardTitle>从类目继续往下走</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <FlowLink
                title="去看商品机会"
                desc="比如你已经看完家电类目，现在先看这个类目下哪些具体商品更值得继续做。"
                href={`${ROUTES.insightsOpportunities}?category=${encodeURIComponent(topCategories[0]?.name || "家电")}`}
                label="进入商品机会页"
              />
              <FlowLink
                title="去看供应链结果"
                desc="如果你已经跑过任务，就去看 1688 供应链结果和匹配情况。"
                href={ROUTES.actionSuppliers}
                label="进入供应链页"
              />
              <FlowLink
                title="去看利润复核"
                desc="当你已经有候选商品时，继续看利润和风险判断。"
                href={ROUTES.actionProfit}
                label="进入利润页"
              />
            </CardContent>
          </Card>
        </div>

        <Card className="border-white/8 bg-[#111A2E] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <CardHeader>
            <CardTitle>最新进入系统的商品</CardTitle>
          </CardHeader>
          <CardContent>
            {latestProducts.length ? (
              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                {latestProducts.map((item) => (
                  <div key={`${item.id}-${item.title}`} className="rounded-2xl border border-white/8 bg-white/5 p-4">
                    <div className="text-base font-semibold text-white">{item.title}</div>
                    <div className="mt-2 text-sm text-white/60">价格：{item.price}</div>
                    <div className="mt-2 text-sm text-white/60">类目：{item.category_name || "未分类"}</div>
                    <div className="mt-2 text-sm text-white/60">进入时间：{item.created_at.replace("T", " ")}</div>
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState text="当前还没有最新商品结果。先去跑一轮真实任务，类目页才会越来越像真正的市场工作台。" />
            )}
          </CardContent>
        </Card>
      </div>
    </XBorderLayout>
  );
}

function MetricTile({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/8 bg-white/5 px-4 py-4">
      <div className="text-sm text-white/45">{label}</div>
      <div className="mt-2 text-lg font-semibold text-white">{value}</div>
    </div>
  );
}

function InfoLine({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-3 rounded-2xl border border-white/8 bg-white/5 px-4 py-3">
      <span className="text-sm text-white/45">{label}</span>
      <span className="text-sm font-medium text-white">{value}</span>
    </div>
  );
}

function FlowLink({
  title,
  desc,
  href,
  label,
}: {
  title: string;
  desc: string;
  href: string;
  label: string;
}) {
  return (
    <Link
      href={href}
      className="block rounded-2xl border border-white/8 bg-white/5 p-4 transition hover:border-[#4F7CFF]/30 hover:bg-[#4F7CFF]/10"
    >
      <div className="text-base font-semibold text-white">{title}</div>
      <div className="mt-2 text-sm leading-7 text-white/60">{desc}</div>
      <div className="mt-4 text-sm font-medium text-[#9CC0FF]">{label}</div>
    </Link>
  );
}
