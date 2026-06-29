import { OperationCenter } from "@/components/operation/operation-center";
import { DecisionFlowShell } from "@/components/decision-flow/decision-flow-shell";
import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { loadFlowPageData } from "@/lib/flow-page-data";

export default async function OperationPage() {
  const { lang, products, tasks, sources } = await loadFlowPageData();

  return (
    <XBorderLayout lang={lang} activePath="operation">
      <DecisionFlowShell
        lang={lang}
        activeStep="operation"
        title="商业执行"
        description="把已经通过判断的商品推进到待执行、已执行和状态流转里，让前端形成完整的业务闭环。"
        products={products}
        tasks={tasks}
        sources={sources}
      >
        <OperationCenter lang={lang} />
      </DecisionFlowShell>
    </XBorderLayout>
  );
}
