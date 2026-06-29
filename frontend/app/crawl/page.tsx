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
        title="数据采集"
        description="从真实商品链接开始，把可分析的商品数据带进系统，作为后续分析、市场判断和供应匹配的基础。"
        products={products}
        tasks={tasks}
        sources={sources}
      >
        <CrawlPanel lang={lang} />
      </DecisionFlowShell>
    </XBorderLayout>
  );
}
