"use client";

import { Card } from "@/design-system/components";
import { BusinessTruthRecommendResponse, DecisionRecommendResponse } from "@/lib/types";

export function ResultPanel({
  decision,
  truth,
}: {
  decision?: DecisionRecommendResponse;
  truth?: BusinessTruthRecommendResponse;
}) {
  const actionStyle = getActionLevelStyle(decision?.action_level);
  return (
    <Card className="border-white/8 bg-[#111A2E] p-6">
      <div className="space-y-6">
        <div>
          <div className="text-xs uppercase tracking-[0.24em] text-white/40">商航AI · AI商业结论</div>
          <h3 className="mt-2 text-xl font-semibold text-white">这次 AI 商业判断给出的核心结论</h3>
        </div>

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <Metric title="综合判断" value={decision?.final_score ?? "—"} />
          <Metric title="AI进入建议" value={decision?.recommendation ?? "—"} />
          <Metric title="利润空间预测" value={truth ? `${truth.profit}` : "—"} />
          <Metric title="数据真实性等级" value={truth?.truth_level ?? decision?.truth_level ?? "—"} />
          <Metric title="可信度" value={decision?.confidence_score ?? "—"} />
          <Metric title="风险等级" value={truth?.truth_recommendation ?? "—"} />
          <Metric title="推进等级" value={decision?.action_level ?? "—"} tone={actionStyle} />
          <Metric title="当前执行状态" value={decision?.platform_execution_status ?? "—"} />
        </div>

        <div className="grid gap-4 xl:grid-cols-2">
          <div className="rounded-2xl border border-white/8 bg-white/5 p-4 xl:col-span-2">
            <div className="text-sm font-medium text-white">动作执行结果</div>
            <div className="mt-3 grid gap-2 text-sm text-white/65 md:grid-cols-2">
              <Row label="推进等级" value={decision?.action_level} valueClassName={actionStyle.textClass} />
              <Row label="拦截原因" value={decision?.execution_block_reason || "—"} />
              <Row label="平台执行状态" value={decision?.platform_execution_status} />
              <Row label="执行队列状态" value={decision?.execution_queue_status} />
            </div>
          </div>
          <div className="rounded-2xl border border-white/8 bg-white/5 p-4">
            <div className="text-sm font-medium text-white">机会判断</div>
            <div className="mt-3 space-y-2 text-sm text-white/65">
              <Row label="市场匹配" value={decision?.market_fit_score} />
              <Row label="供应稳定性" value={decision?.supplier_fit_score} />
              <Row label="利润空间预测" value={decision?.profit_score} />
              <Row label="风险指数" value={decision?.risk_score} />
            </div>
          </div>
          <div className="rounded-2xl border border-white/8 bg-white/5 p-4">
            <div className="text-sm font-medium text-white">利润与可行性</div>
            <div className="mt-3 space-y-2 text-sm text-white/65">
              <Row label="售价" value={truth?.selling_price} />
              <Row label="总成本" value={truth?.total_cost} />
              <Row label="利润率" value={truth ? `${(truth.profit_margin * 100).toFixed(2)}%` : "—"} />
              <Row label="利润建议" value={truth?.truth_recommendation} />
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
}

function Metric({ title, value, tone }: { title: string; value: string | number; tone?: { cardClass: string; textClass: string } }) {
  return (
    <div className={`rounded-2xl border p-4 ${tone?.cardClass ?? "border-white/8 bg-white/5"}`}>
      <div className="text-xs text-white/45">{title}</div>
      <div className={`mt-2 text-2xl font-semibold ${tone?.textClass ?? "text-white"}`}>{String(value)}</div>
    </div>
  );
}

function Row({ label, value, valueClassName }: { label: string; value: string | number | null | undefined; valueClassName?: string }) {
  return (
    <div className="flex items-center justify-between gap-3">
      <span>{label}</span>
      <span className={`font-medium ${valueClassName ?? "text-white"}`}>{value == null ? "—" : String(value)}</span>
    </div>
  );
}


function getActionLevelStyle(actionLevel?: string | null) {
  switch ((actionLevel || "").toUpperCase()) {
    case "KILL":
      return { cardClass: "border-red-500/30 bg-red-500/10", textClass: "text-red-300" };
    case "WATCH":
      return { cardClass: "border-white/10 bg-white/5", textClass: "text-white/70" };
    case "TEST":
      return { cardClass: "border-yellow-500/30 bg-yellow-500/10", textClass: "text-yellow-300" };
    case "SCALE":
      return { cardClass: "border-blue-500/30 bg-blue-500/10", textClass: "text-blue-300" };
    case "AUTO_LIST":
      return { cardClass: "border-green-500/30 bg-green-500/10", textClass: "text-green-300" };
    default:
      return { cardClass: "border-white/8 bg-white/5", textClass: "text-white" };
  }
}
