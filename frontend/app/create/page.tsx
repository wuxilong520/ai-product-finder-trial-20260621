"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { Button, Card, Input } from "@/design-system/components";
import { taskDetailRoute } from "@/config/routes";
import { submitTask } from "@/lib/api/task";
import { getToken } from "@/lib/auth";
import { Language } from "@/lib/i18n";

export default function CreateTaskPage() {
  const router = useRouter();
  const [keyword, setKeyword] = useState("");
  const [marketType, setMarketType] = useState<"amazon" | "1688" | "shopee">("amazon");
  const [supplierStrategy, setSupplierStrategy] = useState<"cheapest" | "quality" | "balanced">("balanced");
  const [costMode, setCostMode] = useState<"strict" | "estimated">("estimated");
  const [decisionMode, setDecisionMode] = useState<"fast" | "deep">("deep");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const token = getToken();
      const result = await submitTask(
        {
          keyword,
          market_type: marketType,
          supplier_strategy: supplierStrategy,
          cost_mode: costMode,
          decision_mode: decisionMode,
        },
        token
      );
      router.push(taskDetailRoute(result.task_id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "创建任务失败");
    } finally {
      setLoading(false);
    }
  }

  return (
    <XBorderLayout lang={"zh" as Language} activePath="action">
      <div className="space-y-6">
        <Card className="border-white/8 bg-[#111A2E] p-6">
          <div className="text-xs uppercase tracking-[0.24em] text-white/40">Create Task</div>
          <h1 className="mt-2 text-3xl font-bold text-white">创建一个新的 AI 决策任务</h1>
          <p className="mt-3 max-w-2xl text-sm leading-7 text-white/55">
            提交后不会同步等结果，而是直接进入任务详情页，由系统后台继续跑。
          </p>
        </Card>

        <Card className="border-white/8 bg-[#111A2E] p-6">
          <form className="space-y-5" onSubmit={handleSubmit}>
            <Field label="关键词">
              <Input value={keyword} onChange={(event) => setKeyword(event.target.value)} placeholder="例如：lip kit" />
            </Field>
            <Field label="市场类型">
              <select
                value={marketType}
                onChange={(event) => setMarketType(event.target.value as "amazon" | "1688" | "shopee")}
                className="flex h-12 w-full rounded-2xl border border-white/10 bg-white/5 px-4 text-sm text-white outline-none"
              >
                <option value="amazon">amazon</option>
                <option value="1688">1688</option>
                <option value="shopee">shopee</option>
              </select>
            </Field>
            <Field label="供应策略">
              <select
                value={supplierStrategy}
                onChange={(event) => setSupplierStrategy(event.target.value as "cheapest" | "quality" | "balanced")}
                className="flex h-12 w-full rounded-2xl border border-white/10 bg-white/5 px-4 text-sm text-white outline-none"
              >
                <option value="cheapest">cheapest</option>
                <option value="quality">quality</option>
                <option value="balanced">balanced</option>
              </select>
            </Field>
            <Field label="成本模式">
              <select
                value={costMode}
                onChange={(event) => setCostMode(event.target.value as "strict" | "estimated")}
                className="flex h-12 w-full rounded-2xl border border-white/10 bg-white/5 px-4 text-sm text-white outline-none"
              >
                <option value="strict">strict</option>
                <option value="estimated">estimated</option>
              </select>
            </Field>
            <Field label="决策模式">
              <select
                value={decisionMode}
                onChange={(event) => setDecisionMode(event.target.value as "fast" | "deep")}
                className="flex h-12 w-full rounded-2xl border border-white/10 bg-white/5 px-4 text-sm text-white outline-none"
              >
                <option value="fast">fast</option>
                <option value="deep">deep</option>
              </select>
            </Field>

            {error ? (
              <div className="rounded-2xl border border-[#FF5C5C]/20 bg-[#FF5C5C]/10 px-4 py-3 text-sm text-[#FFD2D2]">
                {error}
              </div>
            ) : null}

            <Button type="submit" disabled={loading || !keyword.trim()}>
              {loading ? "创建中..." : "创建任务"}
            </Button>
          </form>
        </Card>
      </div>
    </XBorderLayout>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="space-y-2">
      <div className="text-sm font-medium text-white">{label}</div>
      {children}
    </div>
  );
}
