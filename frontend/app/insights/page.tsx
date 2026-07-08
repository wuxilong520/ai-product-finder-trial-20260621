import { MarketAnalysisCard } from "@/components/market/market-analysis-card";
import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/design-system/components";
import { loadFlowPageData } from "@/lib/flow-page-data";

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
            <CardTitle>市场智能页</CardTitle>
            <p className="text-sm leading-7 text-white/55">
              这一页是整个选品流程的第一层入口。先判断这个类目或商品方向到底有没有需求、趋势是不是在涨、竞争是不是太强，再决定要不要继续往商品机会、供应链和利润页推进。
            </p>
          </CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-4">
            <MetricCard label="先看需求" value="有没有市场" />
            <MetricCard label="再看趋势" value="最近是涨是跌" />
            <MetricCard label="再看竞争" value="能不能切进去" />
            <MetricCard label="最后结论" value="继续做还是放弃" />
          </CardContent>
        </Card>

        <Card className="border-white/6 bg-[#111A2E]">
          <CardHeader>
            <CardTitle>这一页之后会接到哪里</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-3">
            <MetricCard label="市场结论好" value="进入商品机会页" />
            <MetricCard label="再往后" value="进入 1688 供应链匹配" />
            <MetricCard label="最后" value="进入利润决策和上架" />
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
