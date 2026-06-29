"use client";

import Link from "next/link";
import { ArrowRight, BrainCircuit, ShoppingBag, Sparkles } from "lucide-react";

import { ROUTES, productDetailRoute } from "@/config/routes";
import { DecisionFlowMiniStatus, DecisionFlowResultBoard, DecisionFlowShell } from "@/components/decision-flow/decision-flow-shell";
import { Badge, Button, Card, CardContent, CardDescription, CardHeader, CardTitle, EmptyState, InfoTile, StatusBadge } from "@/design-system/components";
import { Language, t } from "@/lib/i18n";
import type {
  DashboardSourcesResponse,
  DashboardSummaryResponse,
  DashboardTasksResponse,
  DashboardTrendsResponse,
  P5RankingsResponse,
  P5RecommendationsResponse,
  ProductListResponse,
} from "@/lib/types";

export function DashboardCommandCenter({
  lang,
  summary,
  tasks,
  sources,
  products,
  rankings,
  recommendations,
  isAdmin,
}: {
  lang: Language;
  summary: DashboardSummaryResponse;
  tasks: DashboardTasksResponse;
  sources: DashboardSourcesResponse;
  products: ProductListResponse;
  rankings: P5RankingsResponse | null;
  recommendations: P5RecommendationsResponse | null;
  isAdmin: boolean;
}) {
  const text = t(lang);
  const topRecommendations = recommendations?.items.slice(0, 5) || [];
  const salesMetric = Number(summary.cards.find((item) => item.key === "products")?.value || sources.storage.total_products || products.total || 0);
  const aiIndex = topRecommendations.length
    ? Math.round(topRecommendations.reduce((sum, item) => sum + item.recommendation_score, 0) / topRecommendations.length)
    : 0;
  const currentStepLabel =
    tasks.recent_runs.find((item) => item.status === "running")
      ? lang === "zh" ? "正在执行流程" : "Flow running"
      : salesMetric > 0
        ? lang === "zh" ? "等待下一步推进" : "Waiting for next action"
        : lang === "zh" ? "先开始采集" : "Start with crawl";
  const todayDecision = topRecommendations[0];
  const completedCount = tasks.recent_runs.filter((item) => item.status === "success").length;
  const executedProducts = tasks.recent_runs.filter((item) => item.status === "success").slice(0, 5);

  return (
    <DecisionFlowShell
      lang={lang}
      activeStep="decision"
      title={lang === "zh" ? "AI跨境电商单决策流" : "AI cross-border decision flow"}
      description={lang === "zh"
        ? "现在首页不再是模块拼盘，而是整个业务流程的唯一入口：先采集，再分析，再看市场和供应链，最后做 AI 决策并进入执行。"
        : "The dashboard is now the single entry for the full decision flow."}
      products={products}
      tasks={tasks}
      sources={sources}
    >
      <div className="space-y-6">
        <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
          <Card className="border-white/8 bg-[linear-gradient(135deg,rgba(18,28,44,0.98),rgba(10,17,29,0.98))] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <div className="flex flex-wrap items-center gap-3">
                <Badge variant="brand" className="px-4 py-2 text-sm font-medium">
                  <Sparkles className="h-4 w-4" />
                  {lang === "zh" ? "今日推荐决策" : "Today's recommendation"}
                </Badge>
                <StatusBadge status={todayDecision ? "success" : "blocked"} label={todayDecision ? currentStepLabel : (lang === "zh" ? "等待真实数据" : "Waiting for data")} />
              </div>
              <CardTitle className="text-3xl">
                {todayDecision?.title_zh || todayDecision?.title || (lang === "zh" ? "先采集一个真实商品，系统才会开始给推荐" : "Crawl a real product to start recommendations")}
              </CardTitle>
              <CardDescription className="text-sm leading-7 text-white/60">
                {todayDecision
                  ? (lang === "zh" ? "当前最值得推进的商品会出现在这里，你可以直接进入商品详情或执行中心继续流转。" : "The top recommendation appears here first.")
                  : (lang === "zh" ? "现在系统还没有形成足够推荐结果，所以首页会先引导你走通采集到决策的完整链路。" : "The flow starts here once real data arrives.")}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-5">
              <div className="grid gap-4 md:grid-cols-3">
                <InfoTile label={lang === "zh" ? "当前流程状态" : "Flow status"} value={currentStepLabel} />
                <InfoTile label={lang === "zh" ? "AI推荐指数" : "AI index"} value={`${aiIndex} / 100`} />
                <InfoTile label={lang === "zh" ? "已完成推进" : "Completed"} value={String(completedCount)} />
              </div>
              {todayDecision ? (
                <div className="rounded-[24px] border border-white/8 bg-white/[0.03] p-5">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div>
                      <div className="text-base font-medium text-white">{todayDecision.title_zh || todayDecision.title}</div>
                      <div className="mt-2 text-sm text-white/50">{todayDecision.keyword} · {todayDecision.category || text.dashboardUncategorized}</div>
                    </div>
                    <Badge variant={todayDecision.recommendation_score >= 80 ? "success" : todayDecision.recommendation_score >= 60 ? "warning" : "neutral"} className="px-4 py-2 text-sm">
                      {Math.round(todayDecision.recommendation_score)} / 100
                    </Badge>
                  </div>
                  <div className="mt-4 grid gap-4 md:grid-cols-2">
                    <InfoTile label={lang === "zh" ? "预估利润" : "Estimated profit"} value={String(todayDecision.estimated_profit)} />
                    <InfoTile label={lang === "zh" ? "推荐动作" : "Next action"} value={todayDecision.recommendation} />
                  </div>
                  <div className="mt-4 flex flex-wrap gap-3">
                    <Button asChild>
                      <Link href={productDetailRoute(todayDecision.product_id)}>
                        {lang === "zh" ? "查看完整决策" : "Open decision"}
                        <ArrowRight className="ml-2 h-4 w-4" />
                      </Link>
                    </Button>
                    <Button asChild variant="outline">
                      <Link href={ROUTES.operation}>
                        <ShoppingBag className="mr-2 h-4 w-4" />
                        {lang === "zh" ? "进入执行" : "Open operation"}
                      </Link>
                    </Button>
                  </div>
                </div>
              ) : (
                <EmptyState text={lang === "zh" ? "当前还没有形成推荐商品，先从采集商品开始。" : "No recommendation yet. Start from crawl."} />
              )}
            </CardContent>
          </Card>

          <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <CardTitle>{lang === "zh" ? "当前流程状态" : "Flow status center"}</CardTitle>
              <CardDescription>{lang === "zh" ? "你现在卡在哪一步，这里会直接告诉你。" : "Shows the current bottleneck."}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <DecisionFlowMiniStatus lang={lang} tasks={tasks} products={products} />
              <div className="rounded-2xl border border-white/8 bg-white/[0.03] p-4">
                <div className="flex items-center gap-2 text-sm font-medium text-white">
                  <BrainCircuit className="h-4 w-4" />
                  {lang === "zh" ? "当前建议" : "Current suggestion"}
                </div>
                <div className="mt-3 text-sm leading-7 text-white/60">
                  {salesMetric === 0
                    ? (lang === "zh" ? "当前最重要的是先采集真实商品，不然后面的 AI、市场、供应链都没有输入。" : "Crawl real products first.")
                    : topRecommendations.length === 0
                      ? (lang === "zh" ? "现在已有商品，但还没有足够决策结果，建议先跑分析和市场判断。" : "Analyze and validate the market next.")
                      : (lang === "zh" ? "当前已经有推荐商品，可以继续做供应链确认和执行推进。" : "Move to supplier confirmation and execution.")}
                </div>
              </div>
              {isAdmin ? (
                <Button asChild variant="outline" className="w-full">
                  <Link href={ROUTES.systemAdmin}>{lang === "zh" ? "进入系统设置" : "Open admin"}</Link>
                </Button>
              ) : null}
            </CardContent>
          </Card>
        </div>

        <DecisionFlowResultBoard lang={lang} products={products} tasks={tasks} />

        <div className="grid gap-6 xl:grid-cols-3">
          <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <CardTitle>{lang === "zh" ? "市场判断摘要" : "Market summary"}</CardTitle>
              <CardDescription>{lang === "zh" ? "让你先知道市场值不值得继续。" : "Quick market read."}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <InfoTile label={lang === "zh" ? "热门类目数" : "Top categories"} value={String(summary.top_categories.length)} />
              <InfoTile label={lang === "zh" ? "活跃数据源" : "Active sources"} value={String(sources.sources.filter((item) => item.health === "ok").length)} />
              <Button asChild variant="outline" className="w-full">
                <Link href={ROUTES.marketAnalysis}>{lang === "zh" ? "进入市场判断" : "Open market step"}</Link>
              </Button>
            </CardContent>
          </Card>

          <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <CardTitle>{lang === "zh" ? "供应链匹配摘要" : "Supplier summary"}</CardTitle>
              <CardDescription>{lang === "zh" ? "推荐前先确认能不能拿货。" : "Confirm supply before execution."}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <InfoTile label={lang === "zh" ? "数据源平台" : "Platforms"} value={String(sources.sources.length)} />
              <InfoTile label={lang === "zh" ? "供应链可用" : "Available"} value={String(sources.sources.filter((item) => item.health === "ok").length)} />
              <Button asChild variant="outline" className="w-full">
                <Link href={ROUTES.supplier}>{lang === "zh" ? "进入供应链匹配" : "Open supplier step"}</Link>
              </Button>
            </CardContent>
          </Card>

          <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <CardTitle>{lang === "zh" ? "执行推进摘要" : "Execution summary"}</CardTitle>
              <CardDescription>{lang === "zh" ? "把通过判断的商品推进到执行阶段。" : "Move approved products into operation."}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <InfoTile label={lang === "zh" ? "最近完成任务" : "Recent completed"} value={String(executedProducts.length)} />
              <InfoTile label={lang === "zh" ? "可推进推荐" : "Ready recommendations"} value={String(topRecommendations.length)} />
              <Button asChild className="w-full">
                <Link href={ROUTES.operation}>{lang === "zh" ? "进入执行运营" : "Open operation step"}</Link>
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </DecisionFlowShell>
  );
}

function EmptyBlock({ text }: { text: string }) {
  return <div className="rounded-[16px] border border-dashed border-white/10 bg-white/[0.02] px-4 py-8 text-center text-sm text-white/40">{text}</div>;
}
