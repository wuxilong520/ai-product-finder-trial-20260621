"use client";

import Link from "next/link";
import { ArrowRight, BrainCircuit, CheckCircle2, Clock3, PackageSearch, ScanSearch, ShoppingBag, Truck } from "lucide-react";

import { Badge, Button, Card, CardContent, CardDescription, CardHeader, CardTitle, EmptyState, InfoTile, StatusBadge } from "@/design-system/components";
import { ROUTES } from "@/config/routes";
import { Language } from "@/lib/i18n";
import type { DashboardSourcesResponse, DashboardTasksResponse, ProductListResponse } from "@/lib/types";

export type DecisionFlowStepStatus = "done" | "active" | "pending";

export type DecisionFlowStep = {
  key: "crawl" | "analyze" | "market" | "supplier" | "decision" | "operation";
  title: string;
  description: string;
  href: string;
  status: DecisionFlowStepStatus;
  metricLabel: string;
  metricValue: string;
  actionLabel: string;
};

export function buildDecisionFlowSteps({
  productCount,
  analyzeCount,
  activeSources,
  runningTasks,
  lang,
  activeStep,
}: {
  productCount: number;
  analyzeCount: number;
  activeSources: number;
  runningTasks: number;
  lang: Language;
  activeStep: DecisionFlowStep["key"];
}): DecisionFlowStep[] {
  const orderedKeys: DecisionFlowStep["key"][] = ["crawl", "analyze", "market", "supplier", "decision", "operation"];
  const activeIndex = orderedKeys.indexOf(activeStep);

  const steps: Omit<DecisionFlowStep, "status">[] = [
    {
      key: "crawl",
      title: lang === "zh" ? "采集商品" : "Crawl",
      description: lang === "zh" ? "先拿到真实商品数据，后面所有判断都从这里开始。" : "Start with real product data.",
      href: ROUTES.crawl,
      metricLabel: lang === "zh" ? "已入库商品" : "Products",
      metricValue: String(productCount),
      actionLabel: lang === "zh" ? "进入采集" : "Open crawl",
    },
    {
      key: "analyze",
      title: lang === "zh" ? "商品分析" : "Analyze",
      description: lang === "zh" ? "做 AI 评分、卖点提炼和基础利润判断。" : "Run AI scoring and product analysis.",
      href: ROUTES.analyze,
      metricLabel: lang === "zh" ? "分析结果" : "Analyses",
      metricValue: String(analyzeCount),
      actionLabel: lang === "zh" ? "进入分析" : "Open analyze",
    },
    {
      key: "market",
      title: lang === "zh" ? "市场判断" : "Market",
      description: lang === "zh" ? "看趋势、需求、竞争和机会值。" : "Check trend, demand, competition, and opportunity.",
      href: ROUTES.marketAnalysis,
      metricLabel: lang === "zh" ? "活跃数据源" : "Sources",
      metricValue: String(activeSources),
      actionLabel: lang === "zh" ? "进入市场" : "Open market",
    },
    {
      key: "supplier",
      title: lang === "zh" ? "供应链匹配" : "Supplier",
      description: lang === "zh" ? "找货源、比价格、看匹配度。" : "Match suppliers and compare prices.",
      href: ROUTES.supplier,
      metricLabel: lang === "zh" ? "匹配入口" : "Sources",
      metricValue: String(activeSources),
      actionLabel: lang === "zh" ? "进入供应链" : "Open supplier",
    },
    {
      key: "decision",
      title: lang === "zh" ? "AI决策" : "Decision",
      description: lang === "zh" ? "把商品、市场、供应链结果合成最终判断。" : "Merge product, market, and supplier signals.",
      href: ROUTES.dashboard,
      metricLabel: lang === "zh" ? "运行任务" : "Running",
      metricValue: String(runningTasks),
      actionLabel: lang === "zh" ? "回到决策流" : "Open decision",
    },
    {
      key: "operation",
      title: lang === "zh" ? "执行运营" : "Operation",
      description: lang === "zh" ? "把推荐商品推进到待选、已选、已执行。" : "Move recommendations into execution.",
      href: ROUTES.operation,
      metricLabel: lang === "zh" ? "运行任务" : "Running",
      metricValue: String(runningTasks),
      actionLabel: lang === "zh" ? "进入执行" : "Open operation",
    },
  ];

  return steps.map((step, index) => ({
    ...step,
    status: index < activeIndex ? "done" : index === activeIndex ? "active" : "pending",
  }));
}

export function DecisionFlowShell({
  lang,
  activeStep,
  title,
  description,
  products,
  tasks,
  sources,
  children,
}: {
  lang: Language;
  activeStep: DecisionFlowStep["key"];
  title: string;
  description: string;
  products: ProductListResponse;
  tasks: DashboardTasksResponse;
  sources: DashboardSourcesResponse;
  children: React.ReactNode;
}) {
  const analyzeCount = tasks.recent_runs.filter((item) => item.status === "success").length;
  const runningTasks = tasks.recent_runs.filter((item) => item.status === "running").length;
  const activeSources = sources.sources.filter((item) => item.health === "ok").length;
  const steps = buildDecisionFlowSteps({
    productCount: products.total,
    analyzeCount,
    activeSources,
    runningTasks,
    lang,
    activeStep,
  });

  const currentStep = steps.find((step) => step.key === activeStep) || steps[0];
  const nextStep = steps.find((step) => step.status === "pending");
  const topProducts = products.items.slice(0, 3);

  return (
    <div className="space-y-6">
      <Card className="border-white/8 bg-[linear-gradient(135deg,rgba(18,28,44,0.98),rgba(10,17,29,0.98))] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
        <CardHeader className="gap-5">
          <div className="flex flex-wrap items-center gap-3">
            <Badge variant="brand" className="px-4 py-2 text-sm font-medium">
              <BrainCircuit className="h-4 w-4" />
              {lang === "zh" ? "单决策流" : "Single decision flow"}
            </Badge>
            <StatusBadge
              status={currentStep.status === "done" ? "success" : currentStep.status === "active" ? "running" : "blocked"}
              label={
                currentStep.status === "done"
                  ? lang === "zh" ? "当前步骤已完成" : "Step done"
                  : currentStep.status === "active"
                    ? lang === "zh" ? "当前步骤进行中" : "Current step"
                    : lang === "zh" ? "等待执行" : "Waiting"
              }
            />
          </div>
          <div className="grid gap-5 xl:grid-cols-[1.15fr_0.85fr]">
            <div>
              <CardTitle className="text-3xl">{title}</CardTitle>
              <CardDescription className="mt-3 max-w-3xl text-sm leading-7 text-white/60">{description}</CardDescription>
            </div>
            <div className="grid gap-3 md:grid-cols-3 xl:grid-cols-1">
              <InfoTile label={lang === "zh" ? "当前卡点" : "Current step"} value={currentStep.title} />
              <InfoTile label={lang === "zh" ? "AI推荐指数" : "AI index"} value={`${Math.min(100, 45 + products.total + activeSources * 8)} / 100`} />
              <InfoTile label={lang === "zh" ? "下一步" : "Next"} value={nextStep?.title || (lang === "zh" ? "进入执行" : "Go execute")} />
            </div>
          </div>
        </CardHeader>
      </Card>

      <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
        <CardHeader>
          <CardTitle>{lang === "zh" ? "AI决策流水线" : "AI decision pipeline"}</CardTitle>
          <CardDescription>{lang === "zh" ? "所有功能都收口到这一条业务流程里，不再是分散工具页。" : "Every feature is embedded into one business flow."}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 xl:grid-cols-6">
            {steps.map((step, index) => (
              <div key={step.key} className="relative">
                <FlowNode step={step} />
                {index < steps.length - 1 ? (
                  <div className="pointer-events-none absolute -right-3 top-[50%] hidden h-px w-6 -translate-y-1/2 bg-white/12 xl:block" />
                ) : null}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-6 xl:grid-cols-[1.3fr_0.7fr]">
        <div className="space-y-6">{children}</div>
        <div className="space-y-6">
          <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <CardTitle>{lang === "zh" ? "流程提示" : "Flow guide"}</CardTitle>
              <CardDescription>{lang === "zh" ? "每一步只保留当前决策需要的动作。" : "Only keep the actions needed for the current step."}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <StepGuideRow
                icon={<ScanSearch className="h-4 w-4" />}
                title={lang === "zh" ? "先采集，再分析" : "Crawl first"}
                desc={lang === "zh" ? "没有真实商品数据，后面所有评分都不稳。" : "Without real products, every later score is weak."}
              />
              <StepGuideRow
                icon={<PackageSearch className="h-4 w-4" />}
                title={lang === "zh" ? "分析后再看市场" : "Then check market"}
                desc={lang === "zh" ? "商品本身过关后，再判断市场值不值得做。" : "Validate the product before judging the market."}
              />
              <StepGuideRow
                icon={<Truck className="h-4 w-4" />}
                title={lang === "zh" ? "货源确认后再执行" : "Confirm supply before operation"}
                desc={lang === "zh" ? "能不能拿货、利润够不够，决定最后是否推进。" : "Supplier and margin decide whether to execute."}
              />
            </CardContent>
          </Card>

          <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <CardTitle>{lang === "zh" ? "最近商品" : "Recent products"}</CardTitle>
              <CardDescription>{lang === "zh" ? "从商品中心带进这条决策流的真实商品。" : "Real products entering this flow."}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {topProducts.length ? topProducts.map((product) => (
                <Link key={product.id} href={`${ROUTES.products}/${product.id}`} className="flex items-center justify-between rounded-2xl border border-white/8 bg-white/[0.03] px-4 py-3 transition hover:bg-white/[0.06]">
                  <div className="min-w-0">
                    <div className="truncate text-sm font-medium text-white">{product.title}</div>
                    <div className="mt-1 text-xs text-white/45">{product.title_zh || (lang === "zh" ? "暂无中文标题" : "No translated title")}</div>
                  </div>
                  <ArrowRight className="h-4 w-4 text-white/45" />
                </Link>
              )) : <EmptyState text={lang === "zh" ? "当前还没有商品，请先从采集开始。" : "No products yet. Start from crawl."} />}
            </CardContent>
          </Card>

          <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <CardTitle>{lang === "zh" ? "快捷推进" : "Quick move"}</CardTitle>
              <CardDescription>{lang === "zh" ? "直接去下一步，不再让你在一堆页面里找。" : "Jump to the next step directly."}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {steps.slice(0, 3).map((step) => (
                <Button key={step.key} asChild variant={step.key === activeStep ? "primary" : "outline"} className="w-full justify-between">
                  <Link href={step.href}>
                    {step.title}
                    <ArrowRight className="h-4 w-4" />
                  </Link>
                </Button>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

function FlowNode({ step }: { step: DecisionFlowStep }) {
  const tone =
    step.status === "done"
      ? "border-emerald-400/20 bg-emerald-400/10"
      : step.status === "active"
        ? "border-cyan-400/20 bg-cyan-400/10"
        : "border-white/8 bg-white/[0.03]";

  return (
    <div className={`h-full rounded-[24px] border p-4 shadow-[0_18px_40px_rgba(0,0,0,0.18)] ${tone}`}>
      <div className="flex items-center justify-between gap-3">
        <div className="text-sm font-semibold text-white">{step.title}</div>
        <StatusBadge
          status={step.status === "done" ? "success" : step.status === "active" ? "running" : "blocked"}
          label={step.status === "done" ? "完成" : step.status === "active" ? "进行中" : "待执行"}
          className="px-2 py-1 text-[11px]"
        />
      </div>
      <div className="mt-3 text-xs leading-6 text-white/60">{step.description}</div>
      <div className="mt-4 rounded-2xl border border-white/8 bg-black/10 px-3 py-3">
        <div className="text-xs text-white/40">{step.metricLabel}</div>
        <div className="mt-1 text-lg font-semibold text-white">{step.metricValue}</div>
      </div>
      <Button asChild variant={step.status === "active" ? "primary" : "outline"} className="mt-4 w-full">
        <Link href={step.href}>{step.actionLabel}</Link>
      </Button>
    </div>
  );
}

function StepGuideRow({
  icon,
  title,
  desc,
}: {
  icon: React.ReactNode;
  title: string;
  desc: string;
}) {
  return (
    <div className="rounded-2xl border border-white/8 bg-white/[0.03] px-4 py-4">
      <div className="flex items-center gap-2 text-sm font-medium text-white">
        {icon}
        {title}
      </div>
      <div className="mt-2 text-sm leading-6 text-white/55">{desc}</div>
    </div>
  );
}

export function DecisionFlowResultBoard({
  lang,
  products,
  tasks,
}: {
  lang: Language;
  products: ProductListResponse;
  tasks: DashboardTasksResponse;
}) {
  const executed = tasks.recent_runs.filter((item) => item.status === "success").slice(0, 5);
  const topProducts = products.items.slice(0, 10);

  return (
    <div className="grid gap-6 xl:grid-cols-3">
      <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)] xl:col-span-2">
        <CardHeader>
          <CardTitle>{lang === "zh" ? "推荐商品 TOP10" : "Top 10 recommendations"}</CardTitle>
          <CardDescription>{lang === "zh" ? "优先推进的真实商品。" : "Real products to push first."}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {topProducts.length ? topProducts.map((product, index) => (
            <Link key={product.id} href={`${ROUTES.products}/${product.id}`} className="flex items-center justify-between rounded-2xl border border-white/8 bg-white/[0.03] px-4 py-3 transition hover:bg-white/[0.06]">
              <div className="min-w-0">
                <div className="text-xs text-white/40">TOP {index + 1}</div>
                <div className="truncate text-sm font-medium text-white">{product.title}</div>
              </div>
              <div className="text-sm text-white/55">{product.current_price ?? "—"}</div>
            </Link>
          )) : <EmptyState text={lang === "zh" ? "还没有推荐商品。" : "No recommendations yet."} />}
        </CardContent>
      </Card>

      <div className="space-y-6">
        <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <CardHeader>
            <CardTitle>{lang === "zh" ? "已执行商品" : "Executed items"}</CardTitle>
            <CardDescription>{lang === "zh" ? "最近成功推进的任务。" : "Recently completed tasks."}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {executed.length ? executed.map((item) => (
              <div key={item.id} className="rounded-2xl border border-white/8 bg-white/[0.03] px-4 py-3">
                <div className="flex items-center justify-between gap-2">
                  <div className="text-sm font-medium text-white">{item.platform_name}</div>
                  <CheckCircle2 className="h-4 w-4 text-emerald-300" />
                </div>
                <div className="mt-2 text-xs text-white/50">{item.request_url}</div>
              </div>
            )) : <EmptyState text={lang === "zh" ? "还没有执行完成的商品。" : "Nothing executed yet."} />}
          </CardContent>
        </Card>

        <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <CardHeader>
            <CardTitle>{lang === "zh" ? "利润机会卡" : "Profit opportunity"}</CardTitle>
            <CardDescription>{lang === "zh" ? "今天最值得优先处理的方向。" : "Today's best opportunity."}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <InfoTile label={lang === "zh" ? "建议动作" : "Suggested action"} value={lang === "zh" ? "先完成采集，再推进分析与供应链" : "Finish crawl, then analyze and match supply"} />
            <InfoTile label={lang === "zh" ? "当前重心" : "Current focus"} value={lang === "zh" ? "优先推进高评分商品" : "Push high-score products first"} />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export function DecisionFlowMiniStatus({
  lang,
  tasks,
  products,
}: {
  lang: Language;
  tasks: DashboardTasksResponse;
  products: ProductListResponse;
}) {
  const runningTasks = tasks.recent_runs.filter((item) => item.status === "running").length;
  const doneTasks = tasks.recent_runs.filter((item) => item.status === "success").length;

  return (
    <div className="grid gap-4 md:grid-cols-3">
      <InfoTile label={lang === "zh" ? "商品总数" : "Products"} value={String(products.total)} />
      <InfoTile label={lang === "zh" ? "进行中" : "Running"} value={String(runningTasks)} />
      <InfoTile label={lang === "zh" ? "已完成" : "Completed"} value={String(doneTasks)} />
    </div>
  );
}

export function getFlowActiveFromPath(path: string): "dashboard" | "products" | "admin" {
  if (path.startsWith("/system/admin")) {
    return "admin";
  }
  if (path.startsWith("/product")) {
    return "products";
  }
  return "dashboard";
}

export function getStepKeyFromPath(path: string): DecisionFlowStep["key"] {
  if (path.startsWith("/crawl")) return "crawl";
  if (path.startsWith("/analyze")) return "analyze";
  if (path.startsWith("/market-analysis")) return "market";
  if (path.startsWith("/supplier")) return "supplier";
  if (path.startsWith("/operation")) return "operation";
  return "decision";
}

export function getFlowIcon(stepKey: DecisionFlowStep["key"]) {
  switch (stepKey) {
    case "crawl":
      return <ScanSearch className="h-4 w-4" />;
    case "analyze":
      return <BrainCircuit className="h-4 w-4" />;
    case "market":
      return <Clock3 className="h-4 w-4" />;
    case "supplier":
      return <Truck className="h-4 w-4" />;
    case "operation":
      return <ShoppingBag className="h-4 w-4" />;
    default:
      return <PackageSearch className="h-4 w-4" />;
  }
}
