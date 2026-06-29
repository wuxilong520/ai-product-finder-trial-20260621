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
        title="第3步：做市场判断"
        description="当商品本身看起来还不错时，这一步帮你判断市场到底值不值得进：看趋势、需求、竞争和机会，再决定要不要继续推进。"
        products={products}
        tasks={tasks}
        sources={sources}
      >
        <MarketAnalysisCard lang={lang} />
      </DecisionFlowShell>
    </XBorderLayout>
  );
}
