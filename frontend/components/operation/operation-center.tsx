"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AlertTriangle, CheckCircle2, Clock3, Loader2, Rocket, Sparkles, TrendingUp } from "lucide-react";

import { ActionCard, Badge, Button, Card, CardContent, CardHeader, CardTitle, EmptyState, InfoTile, KpiTile, SectionIntro, StatusBadge } from "@/design-system/components";
import { FeatureGateModal } from "@/components/billing/feature-gate-modal";
import { ROUTES, productDetailRoute } from "@/config/routes";
import { getDashboardTasks, getP5Recommendations } from "@/lib/api-gateway";
import { getToken } from "@/lib/auth";
import { Language, t } from "@/lib/i18n";
import type { DashboardTasksResponse, P5RecommendationsResponse } from "@/lib/types";

export function OperationCenter({ lang }: { lang: Language }) {
  const text = t(lang);
  const uiText = lang === "en"
    ? {
        badge: "Action Center",
        flow: "Execution Flow",
        queueTitle: "Products to Process",
        launched: "Launched",
        selected: "Selected",
        pending: "Pending",
        add: "Add to Store",
        view: "View Product",
        progress: "Progress",
        steps: "Execution Steps",
      }
    : {
        badge: "每日工作台",
        flow: "执行推进流程",
        queueTitle: "待推进商品",
        launched: "已上架",
        selected: "已选",
        pending: "待选",
        add: "一键加入店铺",
        view: "查看商品",
        progress: "推进状态",
        steps: "执行步骤",
      };
  const flowSteps = [text.operationStep1, text.operationStep2, text.operationStep3, text.operationStep4];
  const [data, setData] = useState<P5RecommendationsResponse | null>(null);
  const [tasks, setTasks] = useState<DashboardTasksResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [launchedIds, setLaunchedIds] = useState<number[]>([]);
  const [gateOpen, setGateOpen] = useState(false);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError("");
      try {
        const token = getToken();
        const [result, taskResult] = await Promise.all([
          getP5Recommendations({ limit: 5 }, token),
          getDashboardTasks(token).catch(() => null),
        ]);
        if (!cancelled) {
          setData(result);
          setTasks(taskResult);
        }
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : text.operationLoadFailed);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    void load();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="space-y-5">
      <FeatureGateModal
        open={gateOpen}
        onClose={() => setGateOpen(false)}
        title="这个功能需要开通更高权限"
        description="当前这一键加入店铺还没有对接你的真实店铺系统。你确认后会跳到充值页面；如果不确认，就继续留在当前页面。"
        requiredPlan="pro / enterprise"
        confirmLabel="确认并去开通"
      />
      <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
        <CardContent className="p-6">
          <SectionIntro
            eyebrow="商航AI · 每日工作首页"
            title="把今天该看的机会、商品、采购建议和任务放在一个地方"
            description="这页只保留用户每天真会用到的东西：今日机会、待分析商品、采购建议、风险提醒、AI 任务和快捷入口。不展示技术字段。"
          />
          <div className="mt-5 grid gap-4 md:grid-cols-4">
          {flowSteps.map((step, index) => (
            <div key={step} className="rounded-2xl border border-white/8 bg-white/[0.03] p-4">
              <div className="text-xs uppercase tracking-[0.18em] text-white/35">Step {index + 1}</div>
              <div className="mt-2 text-sm font-medium text-white">{step}</div>
            </div>
          ))}
          </div>
        </CardContent>
      </Card>

      {loading ? (
        <div className="flex min-h-[220px] items-center justify-center text-white/70"><Loader2 className="mr-2 h-5 w-5 animate-spin" />{text.operationLoading}</div>
      ) : error ? (
        <EmptyState title="读取今日工作数据失败" text={error} />
      ) : data?.items.length ? (
        <>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
          <KpiTile label="今日机会" value={`${data.items.length} 个`} hint="今天值得先继续看的商品机会" />
          <KpiTile label="待分析商品" value={String(data.items.filter((item) => item.recommendation_score < 70).length)} hint="还需要进一步判断的商品数量" />
          <KpiTile label="采购建议" value={topSuggestion(data.items)} hint="先看今天最值得推进的动作" />
          <KpiTile label="风险提醒" value={String(riskCount(data.items))} hint="建议你先留意高风险或低分商品" />
          <KpiTile label="AI任务" value={String(tasks?.recent_runs.length || 0)} hint="最近真实跑过的 AI 任务数量" />
        </div>

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <ActionCard title="发现今日机会" description="先看今天最值得推进的商品机会。" href={ROUTES.insightsOpportunities} label="去机会页" badge="今日优先" />
          <ActionCard title="进入采购方案" description="继续筛真实商品、成本、利润和风险。" href={ROUTES.actionProcurement} label="去采购方案" />
          <ActionCard title="查看供应商" description="继续比较供应稳定性、MOQ 和采购建议。" href={ROUTES.actionSuppliers} label="去供应链页" />
          <ActionCard title="看 AI 分析任务" description="打开最近任务，直接看结论和下一步建议。" href={ROUTES.tasks} label="去任务页" />
        </div>

        <div className="grid gap-5 xl:grid-cols-[1.2fr_0.8fr]">
          <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <CardTitle>今日机会与待分析商品</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {data.items.map((item) => {
                const isSelected = selectedIds.includes(item.product_id);
                const isLaunched = launchedIds.includes(item.product_id);
                const statusLabel = isLaunched ? uiText.launched : isSelected ? uiText.selected : uiText.pending;
                return (
                  <Card key={item.product_id} className="border-white/8 bg-white/[0.03] shadow-none">
                    <CardContent className="p-5">
                      <div className="flex flex-wrap items-center justify-between gap-3">
                        <div>
                          <div className="text-base font-medium text-white">{item.title_zh || item.title}</div>
                          <div className="mt-1 text-sm text-white/45">{item.keyword}</div>
                        </div>
                        <div className="flex flex-wrap items-center gap-2">
                          <Badge variant={isLaunched ? "success" : isSelected ? "warning" : "neutral"} className="px-3 py-1.5 text-sm">{statusLabel}</Badge>
                          <StatusBadge status={item.recommendation_score >= 70 ? "success" : item.recommendation_score >= 50 ? "warning" : "blocked"} label={item.recommendation} />
                        </div>
                      </div>
                      <div className="mt-4 grid gap-4 md:grid-cols-3">
                        <InfoTile label={text.operationScore} value={`${Math.round(item.recommendation_score)} / 100`} />
                        <InfoTile label={text.operationProfit} value={String(item.estimated_profit)} />
                        <InfoTile label={text.operationCategory} value={item.category || text.operationPending} />
                      </div>
                      <div className="mt-4 flex flex-wrap gap-3">
                        <Button type="button" onClick={() => setSelectedIds((current) => current.includes(item.product_id) ? current : [...current, item.product_id])}>
                          {text.operationConfirm}
                        </Button>
                        <Button type="button" variant="outline" onClick={() => setSelectedIds((current) => current.filter((id) => id !== item.product_id))}>
                          {text.operationObserve}
                        </Button>
                        <Button type="button" variant="ghost" onClick={() => {
                          setGateOpen(true);
                        }}>
                          <CheckCircle2 className="mr-2 h-4 w-4" />
                          {uiText.add}
                        </Button>
                        <Button asChild variant="outline">
                          <Link href={productDetailRoute(item.product_id)}>{uiText.view}</Link>
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </CardContent>
          </Card>

          <div className="space-y-5">
            <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
              <CardHeader>
                <CardTitle>今日工作概览</CardTitle>
              </CardHeader>
              <CardContent className="grid gap-4 md:grid-cols-3 xl:grid-cols-1">
                <InfoTile label={uiText.pending} value={String(data.items.length - selectedIds.length)} />
                <InfoTile label={uiText.selected} value={String(selectedIds.length)} />
                <InfoTile label={uiText.launched} value={String(launchedIds.length)} />
              </CardContent>
            </Card>

            <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
              <CardHeader>
                <CardTitle>采购建议</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {data.items.slice(0, 3).map((item) => (
                  <div key={`suggestion-${item.product_id}`} className="rounded-[16px] border border-white/8 bg-white/[0.03] px-4 py-4">
                    <div className="flex items-start gap-3">
                      <TrendingUp className="mt-1 h-4 w-4 text-[#9CC0FF]" />
                      <div>
                        <div className="text-sm font-medium text-white">{item.title_zh || item.title}</div>
                        <div className="mt-2 text-sm leading-7 text-white/60">
                          建议先看 {item.recommendation}，当前机会指数 {Math.round(item.recommendation_score)}，利润预估 {item.estimated_profit}。
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
              <CardHeader>
                <CardTitle>风险提醒</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {data.items.filter((item) => item.recommendation_score < 60).length ? (
                  data.items.filter((item) => item.recommendation_score < 60).slice(0, 3).map((item) => (
                    <div key={`risk-${item.product_id}`} className="rounded-[16px] border border-amber-400/20 bg-amber-400/10 px-4 py-4 text-sm text-amber-100">
                      <div className="flex items-start gap-3">
                        <AlertTriangle className="mt-0.5 h-4 w-4" />
                        <div>{item.title_zh || item.title} 当前机会指数偏低，建议先观察，不要急着推进。</div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="rounded-[16px] border border-emerald-400/20 bg-emerald-400/10 px-4 py-4 text-sm text-emerald-100">
                    当前今天没有明显的高风险商品提醒。
                  </div>
                )}
              </CardContent>
            </Card>

            <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
              <CardHeader>
                <CardTitle>AI任务</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {tasks?.recent_runs.length ? tasks.recent_runs.slice(0, 4).map((item) => (
                  <div key={item.id} className="rounded-[16px] border border-white/8 bg-white/[0.03] px-4 py-4">
                    <div className="flex items-center justify-between gap-3">
                      <div className="text-sm font-medium text-white">{item.platform_name}</div>
                      <div className="text-xs text-white/40">{item.status}</div>
                    </div>
                    <div className="mt-2 flex items-start gap-3 text-sm text-white/60">
                      <Clock3 className="mt-1 h-4 w-4 text-white/40" />
                      <div className="min-w-0">{item.request_url}</div>
                    </div>
                  </div>
                )) : (
                  <EmptyState title="当前还没有 AI 任务记录" text="等你跑过分析任务后，这里会显示最近任务。" />
                )}
              </CardContent>
            </Card>
          </div>
        </div>
        </>
      ) : (
        <EmptyState title="当前还没有待推进商品" text={text.operationEmpty} />
      )}
    </div>
  );
}

function topSuggestion(items: P5RecommendationsResponse["items"]) {
  if (!items.length) return "暂无";
  const top = [...items].sort((a, b) => b.recommendation_score - a.recommendation_score)[0];
  return top.recommendation || "待判断";
}

function riskCount(items: P5RecommendationsResponse["items"]) {
  return items.filter((item) => item.recommendation_score < 60).length;
}
