"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { PlanAccessPanel } from "@/components/billing/plan-access-panel";
import { UpgradeEntry } from "@/components/billing/upgrade-entry";
import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { Button, Card, Input } from "@/design-system/components";
import { taskDetailRoute } from "@/config/routes";
import type { CurrentBillingStatus } from "@/lib/api/billing";
import { submitTask } from "@/lib/api/task";
import { Language } from "@/lib/i18n";

export function CreateTaskPageClient({
  token,
  lang,
  currentPlan,
  initialCategory,
  initialKeyword,
}: {
  token: string;
  lang: Language;
  currentPlan: CurrentBillingStatus | null;
  initialCategory?: string;
  initialKeyword?: string;
}) {
  const router = useRouter();
  const [selectedCategory, setSelectedCategory] = useState(initialCategory || "");
  const [keyword, setKeyword] = useState(initialKeyword || "");
  const [marketType, setMarketType] = useState<"amazon" | "1688" | "shopify">("amazon");
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
    <XBorderLayout lang={lang} activePath="action">
      <div className="space-y-6">
        <Card className="border-white/8 bg-[#111A2E] p-6">
          <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
            <div>
              <div className="text-xs uppercase tracking-[0.24em] text-white/40">商航AI · 发起任务</div>
              <h1 className="mt-2 text-3xl font-bold text-white">发起一次完整商业闭环任务</h1>
              <p className="mt-3 max-w-2xl text-sm leading-7 text-white/55">
                这里不是单纯填个关键词就结束。你可以把它当成一次完整业务判断的起点：先判断市场，再看商品机会，再看供应链和利润，最后再进入执行准备。
              </p>
              {selectedCategory ? (
                <div className="mt-4 inline-flex rounded-full border border-[#4F7CFF]/20 bg-[#4F7CFF]/10 px-4 py-2 text-sm text-[#D8E3FF]">
                  当前承接类目：{selectedCategory}
                </div>
              ) : null}
            </div>
            <UpgradeEntry label="去充值 / 升级" compact />
          </div>
        </Card>

        <PlanAccessPanel currentPlan={currentPlan} title="这个任务当前会用到的 AI 权限" />

        <Card className="border-white/8 bg-[#111A2E] p-6">
          <div className="grid gap-4 xl:grid-cols-5">
            {[
              { step: "01", title: "先看市场", desc: "这个关键词现在到底有没有需求。" },
              { step: "02", title: "再看单品", desc: "它是不是值得做，而不是只看热度。" },
              { step: "03", title: "接着找货", desc: "后面会继续对接 1688 供应链匹配。" },
              { step: "04", title: "再算利润", desc: "把成本、售价、风险放一起判断。" },
              { step: "05", title: "最后执行", desc: "确认可以做，再进入上架准备链路。" },
            ].map((item) => (
              <div key={item.step} className="rounded-2xl border border-white/8 bg-white/[0.03] p-4">
                <div className="inline-flex rounded-full bg-[#4F7CFF]/12 px-3 py-1 text-xs font-semibold text-[#9CC0FF]">
                  STEP {item.step}
                </div>
                <div className="mt-3 text-base font-semibold text-white">{item.title}</div>
                <p className="mt-2 text-sm leading-6 text-white/60">{item.desc}</p>
              </div>
            ))}
          </div>
        </Card>

        <Card className="border-white/8 bg-[#111A2E] p-6">
          <form className="space-y-5" onSubmit={handleSubmit}>
            <Field label="你当前要做的类目">
              <Input
                value={selectedCategory}
                onChange={(event) => setSelectedCategory(event.target.value)}
                placeholder="例如：家电、宠物、美妆、厨房用品"
              />
            </Field>
            <Field label="你现在要判断的商品关键词">
              <Input value={keyword} onChange={(event) => setKeyword(event.target.value)} placeholder="例如：炒锅、wireless earbuds、pet brush、kitchen organizer" />
            </Field>
            <Field label="你想先从哪个入口开始看">
              <select
                value={marketType}
                onChange={(event) => setMarketType(event.target.value as "amazon" | "1688" | "shopify")}
                className="flex h-12 w-full rounded-2xl border border-white/10 bg-white/5 px-4 text-sm text-white outline-none"
              >
                <option value="amazon">Amazon 市场判断入口</option>
                <option value="1688">1688 供货入口</option>
                <option value="shopify">Shopify 独立站入口</option>
              </select>
            </Field>
            <Field label="供应链策略">
              <select
                value={supplierStrategy}
                onChange={(event) => setSupplierStrategy(event.target.value as "cheapest" | "quality" | "balanced")}
                className="flex h-12 w-full rounded-2xl border border-white/10 bg-white/5 px-4 text-sm text-white outline-none"
              >
                <option value="cheapest">优先低价</option>
                <option value="quality">优先质量</option>
                <option value="balanced">价格质量平衡</option>
              </select>
            </Field>
            <Field label="成本判断模式">
              <select
                value={costMode}
                onChange={(event) => setCostMode(event.target.value as "strict" | "estimated")}
                className="flex h-12 w-full rounded-2xl border border-white/10 bg-white/5 px-4 text-sm text-white outline-none"
              >
                <option value="strict">严格真实成本</option>
                <option value="estimated">估算成本</option>
              </select>
            </Field>
            <Field label="决策深度">
              <select
                value={decisionMode}
                onChange={(event) => setDecisionMode(event.target.value as "fast" | "deep")}
                className="flex h-12 w-full rounded-2xl border border-white/10 bg-white/5 px-4 text-sm text-white outline-none"
              >
                <option value="fast">快速判断</option>
                <option value="deep">深度判断</option>
              </select>
            </Field>

            <div className="rounded-2xl border border-[#4F7CFF]/20 bg-[#4F7CFF]/10 px-4 py-3 text-sm leading-7 text-[#D8E3FF]">
              说人话就是：你先确定类目，比如“家电”，再填一个具体商品，比如“炒锅”。当前系统会真实把商品关键词送进任务流；类目信息现在先在页面承接和引导，不会假装后台已经完整支持类目字段。
            </div>

            {error ? (
              <div className="rounded-2xl border border-[#FF5C5C]/20 bg-[#FF5C5C]/10 px-4 py-3 text-sm text-[#FFD2D2]">
                {error}
              </div>
            ) : null}

            <Button type="submit" disabled={loading || !keyword.trim()}>
              {loading ? "创建中..." : "开始这次商业判断"}
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
