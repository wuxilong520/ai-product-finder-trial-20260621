import { MarketAnalysisCard } from "@/components/market/market-analysis-card";
import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/design-system/components";
import { ROUTES } from "@/config/routes";
import { loadFlowPageData } from "@/lib/flow-page-data";
import Link from "next/link";

export default async function InsightsPage({
  searchParams,
}: {
  searchParams?: Promise<{ productId?: string; keyword?: string }>;
}) {
  const { lang } = await loadFlowPageData();
  const resolvedSearchParams = searchParams ? await searchParams : undefined;
  const productId = resolvedSearchParams?.productId;
  const keyword = resolvedSearchParams?.keyword ? decodeURIComponent(String(resolvedSearchParams.keyword)) : undefined;

  return (
    <XBorderLayout lang={lang} activePath="insights">
      <div className="space-y-6">
        <Card className="border-white/6 bg-[#111A2E]">
          <CardHeader>
            <div className="text-xs uppercase tracking-[0.24em] text-white/40">商航AI · 市场智能页</div>
            <CardTitle>先判断这个方向有没有市场，再决定要不要继续做</CardTitle>
            <p className="text-sm leading-7 text-white/55">
              你现在不需要先看复杂数据。你只需要先知道四件事：有没有需求、趋势是不是在涨、竞争是不是太强、这个方向值不值得继续进入下一步。
            </p>
          </CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-4">
            <MetricCard label="第一步" value="先看有没有需求" />
            <MetricCard label="第二步" value="再看趋势是涨是跌" />
            <MetricCard label="第三步" value="再看竞争能不能切入" />
            <MetricCard label="第四步" value="最后决定要不要继续" />
          </CardContent>
        </Card>

        <Card className="border-white/6 bg-[#111A2E]">
          <CardHeader>
            <CardTitle>市场判断之后你会往哪里走</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-3">
            <FlowJumpCard
              title="市场结果不错"
              desc="继续进入商品机会页，从方向里筛更值得做的单品。"
              href={ROUTES.insightsOpportunities}
              label="进入商品机会页"
            />
            <FlowJumpCard
              title="单品有机会"
              desc="继续去看 1688 货源、价格、评分、MOQ 和发货周期。"
              href={ROUTES.actionSuppliers}
              label="进入供应链页"
            />
            <FlowJumpCard
              title="货源和成本都过关"
              desc="最后进入利润决策页，看值不值得测试上架。"
              href={ROUTES.actionProfit}
              label="进入利润决策页"
            />
          </CardContent>
        </Card>

        <MarketAnalysisCard lang={lang} initialKeyword={keyword || (productId ? String(productId) : undefined)} />
      </div>
    </XBorderLayout>
  );
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/8 bg-white/[0.03] px-4 py-4">
      <div className="text-sm text-white/45">{label}</div>
      <div className="mt-2 text-lg font-semibold text-white">{value}</div>
    </div>
  );
}

function FlowJumpCard({
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
    <Link href={href} className="rounded-2xl border border-white/8 bg-white/[0.03] px-4 py-4 transition hover:border-[#4F7CFF]/30 hover:bg-[rgba(79,124,255,0.06)]">
      <div className="text-base font-semibold text-white">{title}</div>
      <div className="mt-2 min-h-[72px] text-sm leading-7 text-white/58">{desc}</div>
      <div className="mt-4 text-sm font-medium text-[#9CC0FF]">{label}</div>
    </Link>
  );
}
