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
  return (
    <Card className="border-white/8 bg-[#111A2E] p-6">
      <div className="space-y-6">
        <div>
          <div className="text-xs uppercase tracking-[0.24em] text-white/40">Result Panel</div>
          <h3 className="mt-2 text-xl font-semibold text-white">任务结果总览</h3>
        </div>

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <Metric title="最终评分" value={decision?.final_score ?? "—"} />
          <Metric title="推荐结论" value={decision?.recommendation ?? "—"} />
          <Metric title="利润估算" value={truth ? `${truth.profit}` : "—"} />
          <Metric title="真实性等级" value={truth?.truth_level ?? decision?.truth_level ?? "—"} />
          <Metric title="ROI / 可信度" value={decision?.confidence_score ?? "—"} />
          <Metric title="风险等级" value={truth?.truth_recommendation ?? "—"} />
        </div>

        <div className="grid gap-4 xl:grid-cols-2">
          <div className="rounded-2xl border border-white/8 bg-white/5 p-4">
            <div className="text-sm font-medium text-white">Decision Result</div>
            <div className="mt-3 space-y-2 text-sm text-white/65">
              <Row label="市场匹配" value={decision?.market_fit_score} />
              <Row label="供应适配" value={decision?.supplier_fit_score} />
              <Row label="利润分" value={decision?.profit_score} />
              <Row label="风险分" value={decision?.risk_score} />
            </div>
          </div>
          <div className="rounded-2xl border border-white/8 bg-white/5 p-4">
            <div className="text-sm font-medium text-white">Business Truth</div>
            <div className="mt-3 space-y-2 text-sm text-white/65">
              <Row label="售价" value={truth?.selling_price} />
              <Row label="总成本" value={truth?.total_cost} />
              <Row label="利润率" value={truth ? `${(truth.profit_margin * 100).toFixed(2)}%` : "—"} />
              <Row label="商业建议" value={truth?.truth_recommendation} />
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
}

function Metric({ title, value }: { title: string; value: string | number }) {
  return (
    <div className="rounded-2xl border border-white/8 bg-white/5 p-4">
      <div className="text-xs text-white/45">{title}</div>
      <div className="mt-2 text-2xl font-semibold text-white">{String(value)}</div>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string | number | null | undefined }) {
  return (
    <div className="flex items-center justify-between gap-3">
      <span>{label}</span>
      <span className="font-medium text-white">{value == null ? "—" : String(value)}</span>
    </div>
  );
}
