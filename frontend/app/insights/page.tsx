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
        title: "Insights",
        desc: "Review market trends, hot categories, breakout opportunities, risk alerts, and future outlook in one place.",
        trend: "Market Trends",
        category: "Hot Categories",
        ranking: "Best Sellers",
        risk: "Risk Alerts",
        chart: "Charts",
        compare: "Compare",
        dynamic: "Live updates",
        watch: "Watch now",
      }
    : {
        title: "市场洞察",
        desc: "这里统一查看市场趋势、热门类目、爆款机会、风险提示和未来趋势判断。",
        trend: "市场趋势",
        category: "热门类目",
        ranking: "爆款榜单",
        risk: "风险提示",
        chart: "图表展示",
        compare: "横向对比",
        dynamic: "动态更新",
        watch: "实时关注",
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
            <MetricCard label={text.category} value={text.compare} />
            <MetricCard label={text.ranking} value={text.dynamic} />
            <MetricCard label={text.risk} value={text.watch} />
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
