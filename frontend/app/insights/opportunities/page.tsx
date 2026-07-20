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
  const topItems = items.slice(0, 6);

  return (
    <XBorderLayout lang={lang} activePath="insights">
      <div className="space-y-6">
        <Card className="border-white/8 bg-[#111A2E] p-6 shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <div className="flex flex-col gap-5 xl:flex-row xl:items-end xl:justify-between">
            <div className="max-w-3xl">
              <div className="text-xs uppercase tracking-[0.24em] text-white/40">商航AI · 商品机会页</div>
              <h1 className="mt-2 text-3xl font-semibold tracking-tight text-white">
                {category ? `${category} 下面，先筛出更值得继续做的商品` : "先筛出更值得继续做的商品"}
              </h1>
              <p className="mt-3 text-sm leading-7 text-white/60">
                这一页承接市场页。市场页先告诉你这个方向能不能看，这一页再把更值得继续做的单品挑出来，然后才继续去 1688 供应链和利润决策。
              </p>
            </div>
            <div className="grid gap-3 md:grid-cols-3 xl:min-w-[520px]">
              <MetricTile label="当前类目" value={category || "全部类目"} />
              <MetricTile label="候选商品数" value={`${items.length} 个`} />
              <MetricTile label="当前定位" value="单品筛选层" />
            </div>
          </div>
        </Card>

        <Card className="border-white/8 bg-[#111A2E] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <CardHeader>
            <CardTitle>你现在处在哪一步</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-4">
            <StepTile step="01" title="市场已判断" desc="先判断这个类目或词有没有需求和增长。" />
            <StepTile step="02" title="现在筛单品" desc="从这个方向里继续筛更值得做的具体商品。" />
            <StepTile step="03" title="再比 1688 货源" desc="看价格、评分、MOQ 和发货周期能不能承接。" />
            <StepTile step="04" title="最后看利润" desc="再决定值不值得推进到测试和上架。" />
          </CardContent>
        </Card>

        <Card className="border-white/8 bg-[#111A2E] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <CardHeader>
            <CardTitle>这一页到底做什么</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-3">
            <HintCard
              title="先挑商品"
              desc="不是直接去上架，而是先从类目里找更值得继续做的具体商品。"
            />
            <HintCard
              title="先看机会分"
              desc="这里优先看机会评分、利润潜力、风险等级和数据可信度，再决定是否继续推进。"
            />
            <HintCard
              title="再推到供应链"
              desc="看中商品后，继续去 1688 供应链页筛选，再进入利润决策和上架准备。"
            />
          </CardContent>
        </Card>

        <Card className="border-white/8 bg-[#111A2E] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <CardHeader>
            <CardTitle>这一轮最值得优先看的商品</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {topItems.length ? topItems.map((item, index) => (
              <div key={`top-${item.product_id}-${index}`} className="rounded-2xl border border-white/8 bg-white/5 p-4">
                <div className="flex items-center justify-between gap-3">
                  <div className="text-sm font-medium text-white">TOP {index + 1}</div>
                  <div className="rounded-full bg-[#4F7CFF]/12 px-3 py-1 text-xs font-semibold text-[#9CC0FF]">
                    {Math.round(item.recommendation_score)}
                  </div>
                </div>
                <div className="mt-4 text-base font-semibold text-white">{item.title_zh || item.title}</div>
                <div className="mt-2 text-sm text-white/55">关键词：{item.keyword}</div>
                <div className="mt-2 text-sm text-white/55">AI进入建议：{item.recommendation}</div>
                <div className="mt-4 text-sm leading-7 text-white/60">
                  {buildOpportunitySummary(item.recommendation_score, item.estimated_profit, item.category || category || "这个方向")}
                </div>
              </div>
            )) : <EmptyState text="当前还没有形成 TOP 商品推荐结果。" />}
          </CardContent>
        </Card>

        <Card className="border-white/8 bg-[#111A2E] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <CardHeader>
            <CardTitle>先看什么，再决定推不推进</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-3">
            <HintCard title="先看机会分" desc="机会分高，说明这个商品更值得你多花时间继续判断。" />
            <HintCard title="再看利润潜力" desc="利润潜力不行，就算有热度，也未必值得继续做。" />
            <HintCard title="最后看风险和可信度" desc="如果风险偏高，或者可信度太低，就不要急着推进到供应链和上架。" />
          </CardContent>
        </Card>

        <Card className="border-white/8 bg-[#111A2E] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <CardHeader>
            <CardTitle>当前更值得继续推进的商品候选</CardTitle>
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
                    <div className="mt-4 rounded-2xl border border-white/8 bg-black/10 p-4 text-sm leading-7 text-white/68">
                      {buildOpportunitySummary(item.recommendation_score, item.estimated_profit, item.category || category || "这个方向")}
                    </div>
                    <div className="mt-4 grid gap-2 md:grid-cols-2">
                      <InfoLine label="机会评分" value={`${Math.round(item.recommendation_score)}/100`} />
                      <InfoLine label="AI进入建议" value={item.recommendation} />
                      <InfoLine label="利润潜力" value={item.estimated_profit >= 0 ? "偏正向" : "偏弱"} />
                      <InfoLine
                        label="风险等级"
                        value={
                          item.recommendation_score >= 80
                            ? "低到中"
                            : item.recommendation_score >= 60
                              ? "中等"
                              : "偏高"
                        }
                      />
                      <InfoLine label="预估利润" value={String(item.estimated_profit)} />
                      <InfoLine
                        label="数据可信度"
                        value={
                          item.freshness_score == null
                            ? "当前前端未拿到完整可信度字段"
                            : `${Math.round(Number(item.freshness_score) * 100)}%`
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
                        label="推送到供应链匹配"
                      />
                      <FlowLink
                        href={`${ROUTES.createTask}?category=${encodeURIComponent(item.category || category || "")}&keyword=${encodeURIComponent(item.keyword)}`}
                        label="继续做这个商品的单品判断"
                      />
                      <FlowLink
                        href={ROUTES.actionProfit}
                        label="继续看利润决策"
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
            <CardTitle>这一页看完之后的主流程</CardTitle>
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

function StepTile({ step, title, desc }: { step: string; title: string; desc: string }) {
  return (
    <div className="rounded-2xl border border-white/8 bg-white/5 p-4">
      <div className="text-xs font-semibold uppercase tracking-[0.2em] text-[#9CC0FF]">{step}</div>
      <div className="mt-3 text-base font-semibold text-white">{title}</div>
      <div className="mt-2 text-sm leading-7 text-white/60">{desc}</div>
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

function buildOpportunitySummary(score: number, profit: number, category: string) {
  if (score >= 80 && profit >= 0) {
    return `${category}里这个商品现在更值得优先推进，因为机会分更高，而且利润潜力也没有明显拖后腿。`;
  }
  if (score >= 60) {
    return `${category}里这个商品还有继续观察的价值，但更适合先去看 1688 货源和利润，再决定要不要推进。`;
  }
  return `${category}里这个商品目前不算强机会，更适合先放在备选，不要现在投入太多时间。`;
}
