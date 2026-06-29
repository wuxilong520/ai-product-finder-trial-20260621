import { SupplierCenter } from "@/components/supplier/supplier-center";
import { DecisionFlowShell } from "@/components/decision-flow/decision-flow-shell";
import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { loadFlowPageData } from "@/lib/flow-page-data";

export default async function SupplierPage() {
  const { lang, products, tasks, sources } = await loadFlowPageData();

  return (
    <XBorderLayout lang={lang} activePath="supplier">
      <DecisionFlowShell
        lang={lang}
        activeStep="supplier"
        title="供应网络"
        description="围绕关键词和商品方向匹配供应商，比较价格、可用性和利润空间，帮助你确认供货是否可行。"
        products={products}
        tasks={tasks}
        sources={sources}
      >
        <SupplierCenter lang={lang} />
      </DecisionFlowShell>
    </XBorderLayout>
  );
}
