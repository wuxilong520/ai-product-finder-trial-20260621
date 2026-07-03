import Link from "next/link";

import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { Card, CardContent, CardHeader, CardTitle, EmptyState } from "@/design-system/components";
import { ROUTES } from "@/config/routes";
import { getDashboardTrends } from "@/lib/api-gateway";
import { EMPTY_DASHBOARD_TRENDS, safeLoad } from "@/lib/dashboard-fallback";
import { loadFlowPageData } from "@/lib/flow-page-data";

export default async function InsightsTrendsPage() {
  const { lang, token, tasks, sources } = await loadFlowPageData();
  const trends = await safeLoad(() => getDashboardTrends(token), EMPTY_DASHBOARD_TRENDS);
  const points = trends.series.points;
  const latest = points[points.length - 1];
  const first = points[0];
  const delta = latest && first ? latest.product_count - first.product_count : 0;
  const highPoint = points.reduce(
    (best, item) => (item.product_count > best.product_count ? item : best),
    points[0] || { date: "—", product_count: 0 }
  );

  return (
    <XBorderLayout lang={lang} activePath="insights">
      <div className="space-y-6">
        <Card className="border-white/8 bg-[#111A2E] p-6 shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <div className="flex flex-col gap-5 xl:flex-row xl:items-end xl:justify-between">
            <div className="max-w-3xl">
              <div className="text-xs uppercase tracking-[0.24em] text-white/40">商航AI · 市场趋势页</div>
              <h1 className="mt-2 text-3xl font-semibold tracking-tight text-white">先看趋势是在涨还是在掉，再决定要不要继续做</h1>
              <p className="mt-3 text-sm leading-7 text-white/60">
                如果你是做 Shopify 店铺，第一步不是马上找货，而是先判断这个方向到底有没有增长。这里把当前系统已经沉淀下来的趋势结果单独拉出来，让你先做第一道判断。
              </p>
            </div>
            <div className="grid gap-3 md:grid-cols-4 xl:min-w-[620px]">
              <MetricTile label="趋势周期" value={trends.series.period || "—"} />
              <MetricTile label="趋势点数" value={`${points.length} 个`} />
              <MetricTile label="整体变化" value={delta > 0 ? `+${delta}` : `${delta}`} />
              <MetricTile label="数据来源数" value={`${sources.sources.length} 个`} />
            </div>
          </div>
        </Card>

        <div className="grid gap-6 xl:grid-cols-2">
          <Card className="border-white/8 bg-[#111A2E] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <CardTitle>趋势摘要</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <InfoLine label="最新趋势点" value={latest ? `${latest.date} / ${latest.product_count}` : "暂无"} />
              <InfoLine label="最高趋势点" value={`${highPoint.date} / ${highPoint.product_count}`} />
              <InfoLine label="峰值" value={`${trends.series.peak_value || 0}`} />
              <InfoLine label="任务状态数" value={`${tasks.states.length} 条`} />
              <div className="rounded-2xl border border-white/8 bg-white/5 p-4 text-sm leading-7 text-white/68">
                这里展示的是系统当前已经跑出来的趋势结果，不代表已经接通全网所有平台的实时公开趋势库。
              </div>
            </CardContent>
          </Card>

          <Card className="border-white/8 bg-[#111A2E] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <CardTitle>怎么看这个页面</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {[
                "如果整体变化是增长，你可以继续看具体商品机会。",
                "如果趋势很平，建议先小范围测试，不要直接重投入。",
                "如果趋势明显往下，就先别急着找供应链和上架。",
                "看完趋势后，下一步就该去做具体商品判断。",
              ].map((item) => (
                <div key={item} className="rounded-2xl border border-white/8 bg-white/5 p-4 text-sm leading-7 text-white/68">
                  {item}
                </div>
              ))}
            </CardContent>
          </Card>
        </div>

        <Card className="border-white/8 bg-[#111A2E] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <CardHeader>
            <CardTitle>趋势时间点</CardTitle>
          </CardHeader>
          <CardContent>
            {points.length ? (
              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                {points.map((item) => (
                  <div key={`${item.date}-${item.product_count}`} className="rounded-2xl border border-white/8 bg-white/5 p-4">
                    <div className="text-sm text-white/45">{item.date}</div>
                    <div className="mt-3 text-2xl font-semibold text-white">{item.product_count}</div>
                    <div className="mt-2 text-sm text-white/60">当前趋势值</div>
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState text="当前还没有足够的趋势点。你可以先发起新任务，逐步让趋势页形成更完整的结果。" />
            )}
          </CardContent>
        </Card>

        <Card className="border-white/8 bg-[#111A2E] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <CardHeader>
            <CardTitle>下一步去哪里</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-3">
            <FlowLink
              title="去看热门类目"
              desc="先回到类目页，看看当前系统里哪些类目沉淀结果更多。"
              href={ROUTES.insightsCategories}
              label="进入类目页"
            />
            <FlowLink
              title="去看商品机会"
              desc="比如你已经看完趋势，现在先去看这个方向下哪些具体商品更值得继续做。"
              href={ROUTES.insightsOpportunities}
              label="进入商品机会页"
            />
            <FlowLink
              title="去看供应链"
              desc="如果任务已经有结果，就继续看 1688 供应链匹配。"
              href={ROUTES.actionSuppliers}
              label="进入供应链页"
            />
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
