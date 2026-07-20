"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { PlanAccessPanel } from "@/components/billing/plan-access-panel";
import { UpgradeEntry } from "@/components/billing/upgrade-entry";
import { ExplainPanel } from "@/components/ExplainPanel";
import { ResultPanel } from "@/components/ResultPanel";
import { TaskStatus } from "@/components/TaskStatus";
import { TracePanel } from "@/components/TracePanel";
import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { Button, Card, CardContent, KpiTile, SectionIntro } from "@/design-system/components";
import type { CurrentBillingStatus } from "@/lib/api/billing";
import { getTaskFull, retryTask } from "@/lib/api/task";
import { Language } from "@/lib/i18n";
import { TaskFullResponse } from "@/lib/types";

export function TaskDetailPageClient({
  taskId,
  token,
  lang,
  currentPlan,
}: {
  taskId: number;
  token: string;
  lang: Language;
  currentPlan: CurrentBillingStatus | null;
}) {
  const router = useRouter();
  const [data, setData] = useState<TaskFullResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [retrying, setRetrying] = useState(false);

  async function loadTask() {
    try {
      const result = await getTaskFull(taskId, token);
      setData(result);
      setError("");
      if (result.task.status === "success" || result.task.status === "failed") {
        return true;
      }
      return false;
    } catch (err) {
      setError(err instanceof Error ? err.message : "读取任务失败");
      return true;
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    let stopped = false;
    let timer: ReturnType<typeof setTimeout> | null = null;

    async function poll() {
      const shouldStop = await loadTask();
      if (!stopped && !shouldStop) {
        timer = setTimeout(poll, 2500);
      }
    }

    void poll();
    return () => {
      stopped = true;
      if (timer) clearTimeout(timer);
    };
  }, [taskId]);

  async function handleRetry() {
    try {
      setRetrying(true);
      await retryTask(taskId, token);
      setLoading(true);
      await loadTask();
    } catch (err) {
      setError(err instanceof Error ? err.message : "重试任务失败");
    } finally {
      setRetrying(false);
    }
  }

  return (
    <XBorderLayout lang={lang} activePath="action">
      <div className="space-y-6">
        <Card className="border-white/8 bg-[#111A2E]">
          <CardContent className="p-6">
            <SectionIntro
              eyebrow="商航AI · AI分析报告"
              title={`任务详情 #${taskId}`}
              description="这页已经改成给普通用户看的商业分析报告。你重点看结论、原因、优势、风险和下一步建议，不需要看技术字段。"
              action={(
                <div className="flex items-center gap-3">
                  <UpgradeEntry label="去充值 / 升级" compact />
                  {data?.task.status === "failed" ? (
                    <Button onClick={handleRetry} disabled={retrying}>
                      {retrying ? "重试中..." : "重试任务"}
                    </Button>
                  ) : null}
                  <Button variant="secondary" onClick={() => router.push("/tasks")}>返回任务列表</Button>
                </div>
              )}
            />
          </CardContent>
        </Card>

        <div className="grid gap-4 md:grid-cols-4">
          <KpiTile label="当前状态" value={data?.task.status || "读取中"} hint="先看这次分析是否已经完成" />
          <KpiTile label="核心目标" value="给出可执行建议" hint="不是展示技术日志，而是告诉你值不值得做" />
          <KpiTile label="报告重点" value="结论 / 风险 / 动作" hint="优先看结论和原因" />
          <KpiTile label="当前操作" value={data?.task.status === "failed" ? "可重试" : "查看结果"} hint="失败时可直接重试" />
        </div>

        <PlanAccessPanel currentPlan={currentPlan} title="当前这个任务可调用的 AI 权限" compact />

        {loading && !data ? (
          <div className="rounded-3xl border border-white/8 bg-[#111A2E] p-8 text-white/65">
            正在读取任务状态...
          </div>
        ) : null}

        {error ? (
          <div className="rounded-3xl border border-[#FF5C5C]/20 bg-[#FF5C5C]/10 p-6 text-sm text-[#FFD2D2]">
            {error}
          </div>
        ) : null}

        {data ? (
          <>
            <TaskStatus task={data.task} />
            <ResultPanel decision={data.result?.decision_result} truth={data.result?.truth_result} />
            <BusinessOpportunityPanel data={data} />
            <ExplainPanel explain={data.explain} />
            <TracePanel trace={data.trace} />
          </>
        ) : null}
      </div>
    </XBorderLayout>
  );
}

function BusinessOpportunityPanel({ data }: { data: TaskFullResponse }) {
  const market = data.result?.market_intelligence;
  const marketDetail = market?.market_intelligence;
  const shopifyProducts = data.result?.shopify_real_products || data.result?.shopify_candidates || [];
  const suppliers1688 = data.result?.["1688_real_suppliers"] || data.result?.alibaba_suppliers || [];
  const truth = data.result?.truth_result;
  const decision = data.result?.decision_result;

  return (
    <div className="rounded-3xl border border-white/8 bg-[#111A2E] p-6">
      <div className="text-xs uppercase tracking-[0.24em] text-white/40">商航AI · 商业机会闭环</div>
      <h3 className="mt-2 text-xl font-semibold text-white">这轮任务到底值不值得做</h3>
      <p className="mt-2 text-sm text-white/55">
        这里把商航AI这一轮真正跑出来的市场判断、1688 供货、利润、决策和 Shopify 出口都放在一起，不让你来回猜。
      </p>

      <div className="mt-6 grid gap-4 xl:grid-cols-5">
        <FlowCard
          title="市场需求"
          status={market ? "已生成" : "待补"}
          lines={[
            `市场建议：${showValue(market?.recommendation)}`,
            `市场机会指数：${showValue(market?.market_score)}`,
          ]}
        />
        <FlowCard
          title="1688 匹配"
          status={suppliers1688.length ? "已生成" : "待补"}
          lines={[
            `供应商数：${suppliers1688.length}`,
            `首个报价：${showValue(suppliers1688[0]?.price as string | number | undefined)}`,
          ]}
        />
        <FlowCard
          title="利润空间"
          status={truth ? "已生成" : "待补"}
          lines={[
            `利润：${showValue(truth?.profit)}`,
            `利润率：${truth ? `${(truth.profit_margin * 100).toFixed(2)}%` : "—"}`,
          ]}
        />
        <FlowCard
          title="AI 决策"
          status={decision?.recommendation ? "已生成" : "待补"}
          lines={[
            `结论：${showValue(decision?.recommendation)}`,
            `执行等级：${showValue(decision?.action_level)}`,
          ]}
        />
        <FlowCard
          title="Shopify 出口"
          status={shopifyProducts.length ? "已接通" : "未命中商品"}
          lines={[
            `商品数：${shopifyProducts.length}`,
            `目标平台：${showValue(data.result?.execution_target_platform || decision?.execution_target_platform)}`,
          ]}
        />
      </div>

      <div className="mt-6 grid gap-4 xl:grid-cols-2">
        <DetailCard
          title="市场智能层"
          rows={[
            ["需求分", showValue(marketDetail?.demand_score)],
            ["趋势强度", showValue(marketDetail?.trend_strength)],
            ["竞争等级", showValue(marketDetail?.competition_level)],
            ["市场饱和度", showValue(marketDetail?.market_saturation)],
            ["进入门槛", showValue(marketDetail?.entry_barrier)],
            ["是否为模拟数据", marketDetail?.is_mock ? "是" : "否"],
          ]}
        />
        <DetailCard
          title="平台兼容性"
          rows={[
            ["Shopify 可落地", marketDetail?.platform_compatibility.shopify_ready ? "可以" : "暂不建议"],
            ["TikTok 潜力", showValue(marketDetail?.platform_compatibility.tiktok_potential)],
            ["1688 匹配词", marketDetail?.platform_compatibility.alibaba_match?.join(" / ") || "—"],
            ["Google 信号", showValue(marketDetail?.platform_signals.google_trends_score)],
            ["Amazon 信号", showValue(marketDetail?.platform_signals.amazon_search_volume)],
            ["TikTok 信号", showValue(marketDetail?.platform_signals.tiktok_viral_score)],
          ]}
        />
        <DetailCard
          title="1688 供应链结果"
          rows={[
            ["供应商数", String(suppliers1688.length)],
            ["首个供应商", showValue(String(suppliers1688[0]?.supplier || suppliers1688[0]?.title || "—"))],
            ["首个报价", showValue(suppliers1688[0]?.price as string | number | undefined)],
            ["起订量", showValue(suppliers1688[0]?.moq as string | number | undefined)],
            ["供货来源", showValue(String(suppliers1688[0]?.raw_platform || "—"))],
            ["建议匹配词", marketDetail?.platform_compatibility.alibaba_match?.join(" / ") || "—"],
          ]}
        />
        <DetailCard
          title="Shopify 出口结果"
          rows={[
            ["商品数", String(shopifyProducts.length)],
            ["首个商品", showValue(String(shopifyProducts[0]?.title || "—"))],
            ["商品价格", showValue(shopifyProducts[0]?.price as string | number | undefined)],
            ["库存状态", shopifyProducts[0]?.availability ? "有库存" : "当前无库存"],
            ["平台建议", showValue(data.result?.platform_recommendation)],
            ["发布决定", showValue(data.result?.publish_decision)],
          ]}
        />
      </div>

      <div className="mt-6 grid gap-4 xl:grid-cols-2">
        <ReasonCard
          title="为什么这样判断"
          items={[
            market?.reasoning.demand_reason || "—",
            market?.reasoning.competition_reason || "—",
            market?.reasoning.trend_reason || "—",
          ]}
        />
        <ReasonCard
          title="当前风险提示"
          items={(market?.risk_flags || []).length ? (market?.risk_flags || []) : ["当前没有额外风险标记"]}
        />
      </div>
    </div>
  );
}

function FlowCard({ title, status, lines }: { title: string; status: string; lines: string[] }) {
  return (
    <div className="rounded-2xl border border-white/8 bg-white/5 p-4">
      <div className="flex items-center justify-between gap-3">
        <div className="text-sm font-medium text-white">{title}</div>
        <div className="text-xs text-[#7FDCA4]">{status}</div>
      </div>
      <div className="mt-3 space-y-2 text-sm text-white/65">
        {lines.map((line) => (
          <div key={line}>{line}</div>
        ))}
      </div>
    </div>
  );
}

function DetailCard({ title, rows }: { title: string; rows: Array<[string, string]> }) {
  return (
    <div className="rounded-2xl border border-white/8 bg-white/5 p-4">
      <div className="text-sm font-medium text-white">{title}</div>
      <div className="mt-3 space-y-2 text-sm text-white/65">
        {rows.map(([label, value]) => (
          <div key={`${label}-${value}`} className="flex items-center justify-between gap-3">
            <span>{label}</span>
            <span className="font-medium text-white">{value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function ReasonCard({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="rounded-2xl border border-white/8 bg-white/5 p-4">
      <div className="text-sm font-medium text-white">{title}</div>
      <div className="mt-3 space-y-2 text-sm text-white/65">
        {items.map((item) => (
          <div key={item}>- {item}</div>
        ))}
      </div>
    </div>
  );
}

function showValue(value: string | number | null | undefined) {
  if (value == null || value === "") return "—";
  return String(value);
}
