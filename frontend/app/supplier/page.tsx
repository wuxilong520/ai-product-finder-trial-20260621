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
        title="第4步：确认供应链"
        description="市场值不值得做之后，下一步就是确认能不能拿到货、价格合不合理、利润空间够不够。这里就是整条流程里的供应链确认步骤。"
        products={products}
        tasks={tasks}
        sources={sources}
      >
        <SupplierCenter lang={lang} />
      </DecisionFlowShell>
    </XBorderLayout>
  );
}
