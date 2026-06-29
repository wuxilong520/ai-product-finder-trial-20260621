import { MarketAnalysisCard } from "@/components/market/market-analysis-card";
import { DecisionFlowShell } from "@/components/decision-flow/decision-flow-shell";
import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { loadFlowPageData } from "@/lib/flow-page-data";

export default async function MarketAnalysisPage() {
  const { lang, products, tasks, sources } = await loadFlowPageData();

  return (
    <XBorderLayout lang={lang} activePath="market">
      <DecisionFlowShell
        lang={lang}
        activeStep="market"
        title="市场雷达"
        description="用关键词和商品方向去看趋势、需求、竞争和机会强弱，帮助你判断市场是否值得继续推进。"
        products={products}
        tasks={tasks}
        sources={sources}
      >
        <MarketAnalysisCard lang={lang} />
      </DecisionFlowShell>
    </XBorderLayout>
  );
}
