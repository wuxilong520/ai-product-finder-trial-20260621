import { AnalyzePanel } from "@/components/products/analyze-panel";
import { MarketAnalysisCard } from "@/components/market/market-analysis-card";
import { DecisionFlowShell } from "@/components/decision-flow/decision-flow-shell";
import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { getProduct, isAuthError } from "@/lib/api";
import { loadFlowPageData } from "@/lib/flow-page-data";

export default async function AnalyzePage({
  searchParams,
}: {
  searchParams?: Promise<{ productId?: string }>;
}) {
  const { lang, token, products, tasks, sources } = await loadFlowPageData();
  const resolvedSearchParams = searchParams ? await searchParams : undefined;
  const productId = resolvedSearchParams?.productId;
  let initialUrl: string | undefined;

  if (productId) {
    try {
      const product = await getProduct(productId, token);
      initialUrl = product.source_url;
    } catch (error) {
      if (isAuthError(error)) {
        throw error;
      }
    }
  }

  return (
    <XBorderLayout lang={lang} activePath="analyze">
      <DecisionFlowShell
        lang={lang}
        activeStep="analyze"
        title="第2步：做商品分析"
        description="这一步只干一件事：把采集到的商品变成 AI 可读的判断结果。先看商品本身值不值得做，再进入后面的市场与供应链。"
        products={products}
        tasks={tasks}
        sources={sources}
      >
        <div className="space-y-6">
          <AnalyzePanel initialLang={lang} initialUrl={initialUrl} />
          <MarketAnalysisCard lang={lang} />
        </div>
      </DecisionFlowShell>
    </XBorderLayout>
  );
}
