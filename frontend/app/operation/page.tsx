import { OperationCenter } from "@/components/operation/operation-center";
import { DecisionFlowShell } from "@/components/decision-flow/decision-flow-shell";
import { loadFlowPageData } from "@/lib/flow-page-data";

export default async function OperationPage() {
  const { lang, products, tasks, sources } = await loadFlowPageData();

  return (
    <DecisionFlowShell
      lang={lang}
      activeStep="operation"
      title="第6步：执行运营"
      description="最后一步不再只是看结果，而是把通过判断的商品推进到执行动作里：待选、已选、已执行，真正完成一条业务链路。"
      products={products}
      tasks={tasks}
      sources={sources}
    >
      <OperationCenter lang={lang} />
    </DecisionFlowShell>
  );
}
