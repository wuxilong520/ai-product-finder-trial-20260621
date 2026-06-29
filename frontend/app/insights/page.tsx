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
  const resolvedSearchParams = searchParams ? await searchParams : undefined;
  const productId = resolvedSearchParams?.productId;

  return (
    <XBorderLayout lang={lang} activePath="insights">
      <div className="space-y-6">
        <Card className="border-white/6 bg-[#111A2E]">
          <CardHeader>
            <CardTitle>市场洞察</CardTitle>
            <p className="text-sm leading-7 text-white/55">
              这里统一查看市场趋势、热门类目、爆款机会、风险提示和未来趋势判断。
            </p>
          </CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-4">
            <MetricCard label="市场趋势" value="图表展示" />
            <MetricCard label="热门类目" value="横向对比" />
            <MetricCard label="爆款榜单" value="动态更新" />
            <MetricCard label="风险提示" value="实时关注" />
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
