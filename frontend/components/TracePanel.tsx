"use client";

import { Card } from "@/design-system/components";
import { TaskTraceResponse } from "@/lib/types";

export function TracePanel({ trace }: { trace: TaskTraceResponse["governance_trace"] }) {
  const steps = trace?.lineage_chain?.length
    ? trace.lineage_chain
    : ["source", "provider", "pipeline", "governance", "decision", "result"];

  return (
    <Card className="border-white/8 bg-[#111A2E] p-6">
      <div className="space-y-5">
        <div>
          <div className="text-xs uppercase tracking-[0.24em] text-white/40">执行链路</div>
          <h3 className="mt-2 text-xl font-semibold text-white">这次结论是怎么跑出来的</h3>
        </div>

        <div className="grid gap-3 md:grid-cols-2">
          <div className="rounded-2xl border border-white/8 bg-white/5 p-4 text-sm text-white/70">
            <div>数据编号：<span className="font-medium text-white">{trace?.source_id || "—"}</span></div>
            <div className="mt-2">可信等级：<span className="font-medium text-white">{trace?.truth_level || "—"}</span></div>
          </div>
          <div className="rounded-2xl border border-white/8 bg-white/5 p-4 text-sm text-white/70">
            <div>可信度：<span className="font-medium text-white">{trace?.confidence_score ?? "—"}</span></div>
            <div className="mt-2">新鲜度：<span className="font-medium text-white">{trace?.freshness_score ?? "—"}</span></div>
          </div>
        </div>

        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          <AuditInfo title="事件编号" value={trace?.event_id || "—"} />
          <AuditInfo title="事件键" value={trace?.event_key || "—"} />
          <AuditInfo title="任务编号" value={trace?.task_id ?? "—"} />
          <AuditInfo title="执行阶段" value={trace?.event_stage || "—"} />
          <AuditInfo title="工作区" value={trace?.workspace_id ?? "—"} />
          <AuditInfo title="用户编号" value={trace?.user_id ?? "—"} />
          <AuditInfo title="接口凭证" value={trace?.api_key_id ?? "—"} />
        </div>

        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {steps.map((step, index) => (
            <div key={`${step}-${index}`} className="rounded-2xl border border-white/8 bg-white/5 p-4">
              <div className="text-xs uppercase tracking-[0.22em] text-white/40">Step {index + 1}</div>
              <div className="mt-2 text-sm font-medium text-white">{step}</div>
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
}

function AuditInfo({ title, value }: { title: string; value: string | number }) {
  return (
    <div className="rounded-2xl border border-white/8 bg-white/5 p-4">
      <div className="text-xs uppercase tracking-[0.2em] text-white/40">{title}</div>
      <div className="mt-2 break-all text-sm font-medium text-white">{String(value)}</div>
    </div>
  );
}
