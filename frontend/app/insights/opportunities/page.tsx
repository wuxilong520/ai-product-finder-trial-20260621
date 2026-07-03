import Link from "next/link";

import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { Card, CardContent, CardHeader, CardTitle, EmptyState } from "@/design-system/components";
import { ROUTES } from "@/config/routes";
import { getP5Recommendations } from "@/lib/api-gateway";
import { loadFlowPageData } from "@/lib/flow-page-data";

export default async function InsightsOpportunitiesPage({
  searchParams,
}: {
  searchParams?: Promise<{ category?: string }>;
}) {
  const { lang, token } = await loadFlowPageData();
  const resolvedSearchParams = searchParams ? await searchParams : undefined;
  const category = resolvedSearchParams?.category ? decodeURIComponent(String(resolvedSearchParams.category)) : "";
  const recommendations = await getP5Recommendations(
    {
      category: category || undefined,
      limit: 12,
    },
    token
  ).catch(() => null);

  const items = recommendations?.items || [];

  return (
    <XBorderLayout lang={lang} activePath="insights">
      <div className="space-y-6">
        <Card className="border-white/8 bg-[#111A2E] p-6 shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <div className="flex flex-col gap-5 xl:flex-row xl:items-end xl:justify-between">
            <div className="max-w-3xl">
              <div className="text-xs uppercase tracking-[0.24em] text-white/40">商航AI · 商品机会页</div>
              <h1 className="mt-2 text-3xl font-semibold tracking-tight text-white">
                {category ? `${category} 类目下，先看哪些商品更值得继续做` : "先看哪些商品更值得继续做"}
              </h1>
              <p className="mt-3 text-sm leading-7 text-white/60">
                这一页承接类目页。它不是直接告诉你“马上上架”，而是先把当前系统里更值得继续判断的商品挑出来，再进入供应链匹配、利润决策和上架准备。
              </p>
            </div>
            <div className="grid gap-3 md:grid-cols-3 xl:min-w-[520px]">
              <MetricTile label="当前类目" value={category || "全部类目"} />
              <MetricTile label="机会商品数" value={`${items.length} 个`} />
              <MetricTile label="数据口径" value="系统当前结果" />
            </div>
          </div>
        </Card>

        <Card className="border-white/8 bg-[#111A2E] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <CardHeader>
            <CardTitle>先说明白当前这页看的是什么</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-3">
            <HintCard
              title="看增长机会"
              desc="这里优先展示当前系统综合推荐分更高、利润空间更好的商品方向。"
            />
            <HintCard
              title="不是全网实时大盘"
              desc="当前这页依据的是系统已经沉淀下来的商品、决策、利润结果，不是假装已经接通了所有平台的全网实时商品池。"
            />
            <HintCard
              title="下一步怎么走"
              desc="看中某个商品后，继续去 1688 供应链页筛选，再决定要不要进入利润决策和上架准备。"
            />
          </CardContent>
        </Card>

        <Card className="border-white/8 bg-[#111A2E] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <CardHeader>
            <CardTitle>当前更值得继续看的商品机会</CardTitle>
          </CardHeader>
          <CardContent>
            {items.length ? (
              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                {items.map((item, index) => (
                  <div key={`${item.product_id}-${index}`} className="rounded-2xl border border-white/8 bg-white/5 p-5">
                    <div className="flex items-center justify-between gap-3">
                      <div className="text-sm font-medium text-white">机会 {index + 1}</div>
                      <div className="rounded-full bg-[#4F7CFF]/12 px-3 py-1 text-xs font-semibold text-[#9CC0FF]">
                        {Math.round(item.recommendation_score)}/100
                      </div>
                    </div>
                    <div className="mt-4 text-lg font-semibold text-white">{item.title_zh || item.title}</div>
                    <div className="mt-2 text-sm text-white/55">关键词：{item.keyword}</div>
                    <div className="mt-2 text-sm text-white/55">类目：{item.category || "未分类"}</div>
                    <div className="mt-4 grid gap-2">
                      <InfoLine label="综合推荐" value={item.recommendation} />
                      <InfoLine label="预估利润" value={String(item.estimated_profit)} />
                      <InfoLine
                        label="当前判断"
                        value={
                          item.recommendation_score >= 80
                            ? "优先进入供应链筛选"
                            : item.recommendation_score >= 60
                              ? "可以继续观察和匹配"
                              : "先别急着推进"
                        }
                      />
                    </div>
                    <div className="mt-4 space-y-2 text-sm leading-6 text-white/60">
                      {item.reasons.slice(0, 2).map((reason) => (
                        <div key={reason}>- {reason}</div>
                      ))}
                    </div>
                    <div className="mt-5 grid gap-3">
                      <FlowLink
                        href={`${ROUTES.actionSuppliers}?keyword=${encodeURIComponent(item.keyword)}&category=${encodeURIComponent(item.category || category || "")}`}
                        label="去 1688 供应链匹配"
                      />
                      <FlowLink
                        href={`${ROUTES.createTask}?category=${encodeURIComponent(item.category || category || "")}&keyword=${encodeURIComponent(item.keyword)}`}
                        label="去做这个商品的单品判断"
                      />
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState text={category ? `当前还没有 ${category} 类目下足够的商品机会结果。先继续跑真实任务，这里才会越来越像真正的商品机会页。` : "当前还没有足够的商品机会结果。"} />
            )}
          </CardContent>
        </Card>

        <Card className="border-white/8 bg-[#111A2E] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <CardHeader>
            <CardTitle>下一步主流程</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-3">
            <FlowLink href={ROUTES.insightsCategories} label="回类目市场页" />
            <FlowLink href={ROUTES.actionSuppliers} label="直接去供应链匹配页" />
            <FlowLink href={ROUTES.actionProfit} label="去利润决策页" />
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

function HintCard({ title, desc }: { title: string; desc: string }) {
  return (
    <div className="rounded-2xl border border-white/8 bg-white/5 p-4">
      <div className="text-base font-semibold text-white">{title}</div>
      <div className="mt-2 text-sm leading-7 text-white/60">{desc}</div>
    </div>
  );
}

function InfoLine({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-3 rounded-2xl border border-white/8 bg-black/10 px-4 py-3">
      <span className="text-sm text-white/45">{label}</span>
      <span className="text-sm font-medium text-white">{value}</span>
    </div>
  );
}

function FlowLink({ href, label }: { href: string; label: string }) {
  return (
    <Link
      href={href}
      className="block rounded-2xl border border-white/8 bg-white/5 px-4 py-3 text-sm font-medium text-[#9CC0FF] transition hover:border-[#4F7CFF]/30 hover:bg-[#4F7CFF]/10"
    >
      {label}
    </Link>
  );
}
