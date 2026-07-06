import { MarketAnalysisCard } from "@/components/market/market-analysis-card";
import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/design-system/components";
import { loadFlowPageData } from "@/lib/flow-page-data";

export default async function InsightsPage({
  searchParams,
}: {
  searchParams?: Promise<{ productId?: string }>;
}) {
  const { lang } = await loadFlowPageData();
  const text = lang === "en"
    ? {
        title: "Market Intelligence",
        desc: "This page answers one thing first: does this keyword truly have enough demand to keep going?",
        trend: "Trend Strength",
        demand: "Demand Score",
        competition: "Competition",
        conclusion: "Go / Watch",
        chart: "Need to judge",
        compare: "Need to compare",
        dynamic: "Need confidence",
        watch: "Need conclusion",
      }
    : {
        title: "市场智能页",
        desc: "这一页先回答一件事：这个关键词到底有没有真实市场需求，值不值得继续做下去。",
        trend: "趋势强度",
        demand: "需求判断",
        competition: "竞争强度",
        conclusion: "市场结论",
        chart: "先判断趋势",
        compare: "先判断需求",
        dynamic: "先判断竞争",
        watch: "先给结论",
      };
  const resolvedSearchParams = searchParams ? await searchParams : undefined;
  const productId = resolvedSearchParams?.productId;

  return (
    <XBorderLayout lang={lang} activePath="insights">
      <div className="space-y-6">
        <Card className="border-white/6 bg-[#111A2E]">
          <CardHeader>
            <CardTitle>{text.title}</CardTitle>
            <p className="text-sm leading-7 text-white/55">{text.desc}</p>
          </CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-4">
            <MetricCard label={text.trend} value={text.chart} />
            <MetricCard label={text.demand} value={text.compare} />
            <MetricCard label={text.competition} value={text.dynamic} />
            <MetricCard label={text.conclusion} value={text.watch} />
          </CardContent>
        </Card>

        <Card className="border-white/6 bg-[#111A2E]">
          <CardHeader>
            <CardTitle>这页到底是干什么的</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-3">
            <MetricCard label="第一步" value="先看有没有需求" />
            <MetricCard label="第二步" value="再看竞争强不强" />
            <MetricCard label="第三步" value="最后决定继续还是放弃" />
          </CardContent>
        </Card>

        <MarketAnalysisCard lang={lang} initialKeyword={productId ? String(productId) : undefined} />
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
