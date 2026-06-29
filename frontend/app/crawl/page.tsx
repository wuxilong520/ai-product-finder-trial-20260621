import { CrawlPanel } from "@/components/products/crawl-panel";
import { DecisionFlowShell } from "@/components/decision-flow/decision-flow-shell";
import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { loadFlowPageData } from "@/lib/flow-page-data";

export default async function CrawlPage() {
  const { lang, products, tasks, sources } = await loadFlowPageData();

  return (
    <XBorderLayout lang={lang} activePath="crawl">
      <DecisionFlowShell
        lang={lang}
        activeStep="crawl"
        title="第1步：采集真实商品"
        description="这里不再是独立工具页，而是整条决策流的起点。你先把真实商品抓进系统，后面的 AI 分析、市场判断、供应链匹配、最终决策都会围绕这些商品继续往下走。"
        products={products}
        tasks={tasks}
        sources={sources}
      >
        <CrawlPanel lang={lang} />
      </DecisionFlowShell>
    </XBorderLayout>
  );
}
