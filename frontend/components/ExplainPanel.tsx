"use client";

import { Card } from "@/design-system/components";
import { TaskExplainResponse } from "@/lib/types";

export function ExplainPanel({ explain }: { explain: TaskExplainResponse["explain_result"] }) {
  return (
    <Card className="border-white/8 bg-[#111A2E] p-6">
      <div className="space-y-5">
        <div>
          <div className="text-xs uppercase tracking-[0.24em] text-white/40">AI判断说明</div>
          <h3 className="mt-2 text-xl font-semibold text-white">为什么系统给了这个建议</h3>
        </div>

        <div className="grid gap-3 md:grid-cols-2">
          <Info title="市场来源" value={explain?.market_provider || "—"} />
          <Info title="供应来源" value={explain?.supplier_provider || "—"} />
          <Info title="成本来源" value={explain?.cost_provider || "—"} />
          <Info title="可信度" value={String(explain?.confidence_score ?? "—")} />
        </div>

        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          <Info title="任务编号" value={String(explain?.task_id ?? "—")} />
          <Info title="商品编号" value={String(explain?.product_id ?? "—")} />
          <Info title="接口编号" value={String(explain?.api_key_id ?? "—")} />
          <Info title="链路节点数" value={String(explain?.data_lineage?.length ?? 0)} />
        </div>

        <Section title="市场信号" content={explain?.market_signals_used || []} />
        <Section title="供应候选" content={explain?.supplier_sources || []} />
        <Section title="成本结构" content={explain?.cost_breakdown || {}} />
        <Section title="风险提示" content={explain?.risk_factors || {}} />
        <Section title="来源路径" content={explain?.provider_routing || {}} />

        <div className="rounded-2xl border border-white/8 bg-white/5 p-4 text-sm text-white/70">
          推荐原因：
          <div className="mt-3 space-y-2 text-white/85">
            {(explain?.why_this_recommendation || []).length ? (
              explain?.why_this_recommendation?.map((item, index) => (
                <div key={`${item}-${index}`} className="rounded-xl border border-white/8 bg-white/5 px-3 py-2">
                  {item}
                </div>
              ))
            ) : (
              <div className="text-white/45">当前还没有可展示的解释内容。</div>
            )}
          </div>
        </div>
      </div>
    </Card>
  );
}

function Info({ title, value }: { title: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/8 bg-white/5 p-4">
      <div className="text-xs uppercase tracking-[0.2em] text-white/40">{title}</div>
      <div className="mt-2 text-sm font-medium text-white">{value}</div>
    </div>
  );
}

function Section({ title, content }: { title: string; content: unknown }) {
  return (
    <div className="rounded-2xl border border-white/8 bg-white/5 p-4">
      <div className="text-sm font-medium text-white">{title}</div>
      <pre className="mt-3 overflow-x-auto whitespace-pre-wrap break-all text-xs leading-6 text-white/65">
        {JSON.stringify(content, null, 2)}
      </pre>
    </div>
  );
}
