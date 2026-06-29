import { AnalyzePanel } from "@/components/products/analyze-panel";
import { MarketAnalysisCard } from "@/components/market/market-analysis-card";
import { DecisionFlowShell } from "@/components/decision-flow/decision-flow-shell";
import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { getProduct, isAuthError } from "@/lib/api-gateway";
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
        title="智能分析"
        description="围绕商品本身做 AI 评分、卖点判断和基础机会分析，帮助你更快判断这个商品值不值得继续看。"
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
