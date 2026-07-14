"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useMemo, useState } from "react";
import { ArrowRight, BarChart3, Flame, PackageSearch, ShieldAlert, ShoppingBag, Sparkles, TrendingUp, WalletCards } from "lucide-react";

import { PlanAccessPanel } from "@/components/billing/plan-access-panel";
import { MarketAnalysisCard } from "@/components/market/market-analysis-card";
import { ROUTES, productDetailRoute } from "@/config/routes";
import { ActionCard, Badge, Button, Card, CardContent, CardDescription, CardHeader, CardTitle, EmptyState, InfoTile, Input, KpiTile, SectionIntro } from "@/design-system/components";
import type { CurrentBillingStatus } from "@/lib/api/billing";
import { Language } from "@/lib/i18n";
import type {
  DashboardSourcesResponse,
  DashboardSummaryResponse,
  DashboardTasksResponse,
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
  currentPlan,
}: {
  lang: Language;
  summary: DashboardSummaryResponse;
  tasks: DashboardTasksResponse;
  sources: DashboardSourcesResponse;
  products: ProductListResponse;
  rankings: P5RankingsResponse | null;
  recommendations: P5RecommendationsResponse | null;
  isAdmin: boolean;
  currentPlan: CurrentBillingStatus | null;
}) {
  const router = useRouter();
  const text = lang === "en"
    ? {
        totalProducts: "Total Products",
        totalProductsDesc: "Real products currently inside the system",
        profitChance: "Profit Potential",
        profitChanceDesc: "Estimated profit across recommended products",
        marketHeat: "Market Heat",
        marketHeatDesc: "Combined heat from the growth ranking",
        aiIndex: "AI Decision Index",
        aiIndexDesc: "Average decision score of current recommendations",
        todayTitle: "Today's Key Products",
        todayDesc: "Shows the real products worth reviewing first today.",
        recommendBadge: "Recommended",
        profit: "Profit",
        keyword: "Keyword",
        suggestion: "Suggestion",
        noToday: "No daily recommendations yet. Start by adding real products.",
        categoriesTitle: "Fast-Growing Categories",
        categoriesDesc: "Use real product distribution and growth results to spot stronger directions.",
        categoryBadge: "Category",
        categoryCount: "Products in library:",
        noCategory: "There is not enough category data yet.",
        oppTitle: "Market Opportunities",
        oppDesc: "See which directions are worth deeper judgment now.",
        chance: "Opportunity",
        category: "Category",
        uncategorized: "Uncategorized",
        heat: "Heat",
        risk: "Risk",
        profitRoom: "Profit Room",
        riskLow: "Low to medium",
        riskMid: "Medium",
        riskHigh: "High",
        roomHigh: "Strong",
        roomWatch: "Watch",
        roomCareful: "Careful",
        noOpp: "No clear market opportunity yet.",
      }
    : {
        totalProducts: "总商品量",
        totalProductsDesc: "当前进入系统的真实商品数量",
        profitChance: "利润机会",
        profitChanceDesc: "推荐商品的累计预估利润",
        marketHeat: "市场热度",
        marketHeatDesc: "来自增长榜的综合热度",
        aiIndex: "AI推荐指数",
        aiIndexDesc: "当前推荐商品的平均决策分",
        todayTitle: "今日值得关注商品",
        todayDesc: "这里展示今天最值得优先关注的真实商品。",
        recommendBadge: "推荐",
        profit: "利润",
        keyword: "关键词",
        suggestion: "建议",
        noToday: "现在还没有形成今日推荐商品，先从采集真实商品开始。",
        categoriesTitle: "热门增长类目",
        categoriesDesc: "用真实商品分布和增长结果，快速看当前更值得关注的类目方向。",
        categoryBadge: "类目",
        categoryCount: "当前入库商品数：",
        noCategory: "当前还没有足够类目分布数据。",
        oppTitle: "潜力市场机会",
        oppDesc: "看现在更值得深入判断的机会方向。",
        chance: "机会",
        category: "类目",
        uncategorized: "未分类",
        heat: "热度",
        risk: "风险",
        profitRoom: "利润空间",
        riskLow: "中低",
        riskMid: "中等",
        riskHigh: "偏高",
        roomHigh: "较高",
        roomWatch: "可观察",
        roomCareful: "谨慎",
        noOpp: "当前还没有形成清晰的市场机会结果。",
      };
  const topRecommendations = recommendations?.items.slice(0, 8) || [];
  const categoryCards = summary.top_categories.slice(0, 6);
  const marketOpportunities = rankings?.growth_ranking.top_10.slice(0, 3) || [];
  const riskOpportunities = rankings?.risk_ranking.top_10.slice(0, 3) || [];
  const latestRuns = tasks.recent_runs.slice(0, 3);
  const newestProducts = products.items.slice(0, 4);
  const totalProfit = topRecommendations.reduce((sum, item) => sum + Number(item.estimated_profit || 0), 0);
  const avgAiScore = topRecommendations.length
    ? Math.round(topRecommendations.reduce((sum, item) => sum + item.recommendation_score, 0) / topRecommendations.length)
    : 0;
  const avgMarketHeat = marketOpportunities.length
    ? Math.round(marketOpportunities.reduce((sum, item) => sum + item.score, 0) / marketOpportunities.length)
    : 0;
  const marketStatus = avgMarketHeat >= 70 ? "偏强" : avgMarketHeat >= 45 ? "中等" : "偏弱";
  const profitStatus = totalProfit > 0 ? "有利润空间" : "待形成";
  const riskStatus = riskOpportunities.length
    ? (() => {
        const avgRisk = Math.round(riskOpportunities.reduce((sum, item) => sum + item.score, 0) / riskOpportunities.length);
        if (avgRisk <= 35) return "偏低";
        if (avgRisk <= 65) return "中等";
        return "偏高";
      })()
    : "待判断";
  const defaultKeyword = useMemo(() => {
    if (topRecommendations[0]?.keyword) return topRecommendations[0].keyword;
    if (categoryCards[0]?.name) return categoryCards[0].name;
    return "";
  }, [topRecommendations, categoryCards]);
  const [quickKeyword, setQuickKeyword] = useState(defaultKeyword);

  function pushToInsights() {
    const keyword = quickKeyword.trim();
    router.push(keyword ? `${ROUTES.insights}?keyword=${encodeURIComponent(keyword)}` : ROUTES.insights);
  }

  function pushToCreateTask() {
    const keyword = quickKeyword.trim();
    router.push(keyword ? `${ROUTES.createTask}?keyword=${encodeURIComponent(keyword)}` : ROUTES.createTask);
  }

  const dashboardQuickActions = [
    {
      title: "市场分析页",
      desc: "先判断关键词需求、趋势、竞争和饱和度。",
      href: ROUTES.insights,
      label: "去看市场",
      icon: <BarChart3 className="h-4 w-4" />,
    },
    {
      title: "商品机会页",
      desc: "基于市场结果继续筛商品，找更值得做的方向。",
      href: ROUTES.insightsOpportunities,
      label: "去看机会",
      icon: <Sparkles className="h-4 w-4" />,
    },
    {
      title: "供应链匹配页",
      desc: "继续看 1688 货源、成本和供应稳定性。",
      href: ROUTES.actionSuppliers,
      label: "去看供应链",
      icon: <PackageSearch className="h-4 w-4" />,
    },
    {
      title: "利润决策页",
      desc: "统一看 ROI、利润空间和风险等级。",
      href: ROUTES.actionProfit,
      label: "去看利润",
      icon: <WalletCards className="h-4 w-4" />,
    },
  ];

  const todayOpportunityCount = marketOpportunities.length;
  const procurementCount = newestProducts.length;
  const analysisCount = latestRuns.length;
  const potentialProfit = totalProfit > 0 ? `¥${totalProfit.toFixed(2)}` : "待形成";

  return (
    <div className="space-y-6">
      <Card className="border-white/6 bg-[linear-gradient(135deg,rgba(79,124,255,0.16),rgba(17,26,46,0.95))]">
        <CardContent className="flex flex-col gap-6 p-6 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-3xl">
            <div className="text-xs uppercase tracking-[0.22em] text-[#D8E3FF]">商航AI · 产品功能首页</div>
            <h1 className="mt-3 text-3xl font-semibold tracking-tight text-white lg:text-4xl">
              帮你把“找市场、找货源、算利润、上 Shopify”串成一条线
            </h1>
            <p className="mt-3 text-sm leading-7 text-white/68">
              你不需要先看后台状态。你只需要先判断市场，再筛商品，再匹配 1688 货源，最后决定值不值得上架。首页现在就是按这条路带你走。
            </p>
            <div className="mt-5 flex flex-col gap-3 rounded-2xl border border-white/10 bg-black/10 p-4">
              <div className="text-sm font-medium text-white">一键分析入口</div>
              <div className="text-sm leading-7 text-white/60">
                你已经有想法时，比如“炒锅”“空气炸锅”“电热饭盒”，直接在这里输入，马上进入市场分析或任务创建。
              </div>
              <div className="flex flex-col gap-3 xl:flex-row">
                <Input
                  value={quickKeyword}
                  onChange={(event) => setQuickKeyword(event.target.value)}
                  placeholder="输入你现在要判断的商品关键词"
                  className="xl:max-w-md"
                />
                <div className="flex flex-wrap gap-3">
                  <Button type="button" onClick={pushToInsights}>
                    先做市场分析
                  </Button>
                  <Button type="button" variant="secondary" onClick={pushToCreateTask}>
                    进入商品机会
                  </Button>
                </div>
              </div>
            </div>
          </div>
          <div className="grid gap-3 sm:grid-cols-3 lg:min-w-[420px]">
            <InfoTile label="第一步" value="看市场" />
            <InfoTile label="第二步" value="筛商品" />
            <InfoTile label="第三步" value="比货源" />
          </div>
        </CardContent>
      </Card>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <KpiTile label="今日市场机会" value={`${todayOpportunityCount} 个`} hint="今天优先值得继续看的方向数量" />
        <KpiTile label="采购池商品数量" value={`${procurementCount} 个`} hint="当前首页抓到的最近商品规模" />
        <KpiTile label="AI分析次数" value={`${analysisCount} 次`} hint="最近已经执行过的分析任务数量" />
        <KpiTile label="潜在利润机会" value={potentialProfit} hint="基于当前推荐商品的合计利润空间" />
      </section>

      <section className="grid gap-4 xl:grid-cols-3">
        <ActionCard
          title="我还没想好卖什么"
          description="先从类目和关键词开始，判断这个方向到底有没有增长。"
          href={ROUTES.insights}
          label="先去看市场"
          badge="适合刚开始"
        />
        <ActionCard
          title="我已经有类目方向"
          description="比如你已经决定做家电，那就继续筛到更值得做的具体商品。"
          href={ROUTES.insightsOpportunities}
          label="继续筛商品"
          badge="适合已经有方向"
        />
        <ActionCard
          title="我已经在比货和利润"
          description="说明你已经接近执行，下一步就是对比 1688 货源和利润空间。"
          href={ROUTES.actionSuppliers}
          label="进入供应链匹配"
          badge="适合准备上架"
        />
      </section>

      <Card className="border-white/6 bg-[#111A2E]">
        <CardContent className="p-6">
          <SectionIntro
            eyebrow="Dashboard"
            title="你今天最适合从哪里开始"
            description="如果你是第一次进来，就从市场分析开始。如果你已经有商品方向，就直接进商品机会、采购池和供应链。首页的目标不是堆数据，而是让你 5 秒知道下一步。"
          />
          <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            {dashboardQuickActions.map((item) => (
              <div key={item.title} className="rounded-3xl border border-white/8 bg-white/[0.03] p-5">
                <div className="inline-flex rounded-2xl bg-[#4F7CFF]/12 p-2 text-[#9CC0FF]">{item.icon}</div>
                <div className="mt-4 text-base font-semibold text-white">{item.title}</div>
                <div className="mt-2 text-sm leading-7 text-white/60">{item.desc}</div>
                <Link href={item.href} className="mt-5 inline-flex items-center text-sm font-medium text-[#9CC0FF]">
                  {item.label}
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <section className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
        <Card className="border-white/6 bg-[#111A2E]">
          <CardHeader>
            <CardTitle>今天这个方向值不值得继续做</CardTitle>
            <CardDescription>这块只回答用户最关心的三件事：有没有热度、有没有利润、风险大不大。</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 md:grid-cols-3">
              <StatusMetric
                label="需求热度"
                value={marketStatus}
                desc={marketOpportunities.length ? `当前市场热度均值 ${avgMarketHeat}/100` : "现在还没有形成足够的热度结果"}
                tone={marketStatus === "偏强" ? "green" : marketStatus === "中等" ? "orange" : "neutral"}
              />
              <StatusMetric
                label="利润空间"
                value={profitStatus}
                desc={topRecommendations.length ? `当前推荐商品累计预估利润 ${totalProfit.toFixed(2)}` : "现在还没有形成足够的利润结果"}
                tone={profitStatus === "有利润空间" ? "green" : "neutral"}
              />
              <StatusMetric
                label="进入风险"
                value={riskStatus}
                desc={riskOpportunities.length ? "基于当前机会和竞争结果得出" : "现在还没有形成足够的风险判断"}
                tone={riskStatus === "偏低" ? "green" : riskStatus === "中等" ? "orange" : riskStatus === "偏高" ? "red" : "neutral"}
              />
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              {dashboardQuickActions.map((item) => (
                <QuickEntry
                  key={item.title}
                  title={item.title}
                  desc={item.desc}
                  href={item.href}
                  label={item.label}
                  icon={item.icon}
                />
              ))}
            </div>
            <div className="grid gap-4 xl:grid-cols-2">
              <div className="rounded-2xl border border-white/6 bg-white/[0.03] p-4">
                <div className="text-sm font-medium text-white">为什么今天先看这些</div>
                <div className="mt-4 grid gap-3">
                  {[
                    "先看市场，是为了先判断这个词到底有没有人搜、有没有增长。",
                    "再看商品机会，是为了从类目里找到竞争更低、更适合切入的单品。",
                    "再看供应链，是为了确认 1688 价格、评分、MOQ 和发货周期能不能承接。",
                    "最后看利润和上架，是为了防止刚有点热度就盲目上架。",
                  ].map((item) => (
                    <div key={item} className="rounded-xl border border-white/6 bg-black/10 px-3 py-3 text-sm leading-7 text-white/68">
                      {item}
                    </div>
                  ))}
                </div>
              </div>
              <div className="rounded-2xl border border-white/6 bg-white/[0.03] p-4">
                <div className="text-sm font-medium text-white">今天你可以直接怎么走</div>
                <div className="mt-4 grid gap-3">
                  {[
                    { step: "第一步", text: "如果你还没定商品，就先去市场分析页输入关键词。" },
                    { step: "第二步", text: "如果你已经想做家电，就去商品机会页继续筛单品。" },
                    { step: "第三步", text: "如果单品看起来能做，就去供应链页比 1688 货源。" },
                    { step: "第四步", text: "最后再去利润决策页，看值不值得测试上架。" },
                  ].map((item) => (
                    <div key={item.step} className="rounded-xl border border-white/6 bg-black/10 px-3 py-3">
                      <div className="text-sm font-medium text-[#9CC0FF]">{item.step}</div>
                      <div className="mt-2 text-sm leading-6 text-white/60">{item.text}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <MarketAnalysisCard lang={lang} />
      </section>

      <Card className="border-white/6 bg-[#111A2E]">
        <CardHeader>
          <CardTitle>商航AI 现在是怎么帮你走闭环的</CardTitle>
          <CardDescription>先看市场，再筛商品，再匹配货源，再做利润判断，最后决定要不要推进到上架。</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4 xl:grid-cols-5">
          {[
            ["市场", "先判断类目、关键词、趋势和竞争。"],
            ["商品", "从方向里继续筛更有机会的单品。"],
            ["供应链", "对比 1688 价格、评分、MOQ 和周期。"],
            ["利润", "统一看成本、售价、利润和风险。"],
            ["上架", "等判断通过后，再进入执行和发布。"],
          ].map(([title, desc], index) => (
            <div key={title} className="rounded-2xl border border-white/6 bg-white/[0.03] p-4">
              <div className="text-xs font-semibold uppercase tracking-[0.18em] text-[#9CC0FF]">步骤 {index + 1}</div>
              <div className="mt-3 text-lg font-semibold text-white">{title}</div>
              <div className="mt-2 text-sm leading-7 text-white/60">{desc}</div>
            </div>
          ))}
        </CardContent>
      </Card>

      <section className="grid gap-6 xl:grid-cols-2">
        <Card className="border-white/6 bg-[#111A2E]">
          <CardHeader>
            <CardTitle>今日趋势商品</CardTitle>
            <CardDescription>这块回答的是：今天有哪些真实商品值得你优先点进去看。</CardDescription>
          </CardHeader>
          <CardContent>
            {newestProducts.length ? (
              <div className="grid gap-4 sm:grid-cols-2">
                {newestProducts.map((item) => (
                  <Link
                    key={item.id}
                    href={productDetailRoute(item.id)}
                    className="group rounded-2xl border border-white/6 bg-[rgba(255,255,255,0.02)] p-4 transition hover:-translate-y-0.5 hover:border-[#4F7CFF]/30 hover:bg-[rgba(79,124,255,0.06)]"
                  >
                    <div className="flex items-center justify-between gap-3">
                      <Badge variant="brand" className="px-3 py-1.5 text-xs">
                        今日关注
                      </Badge>
                      <span className="text-xs text-white/45">ID #{item.id}</span>
                    </div>
                    <div className="mt-4 line-clamp-2 min-h-[44px] text-sm font-medium leading-6 text-white">
                      {item.title_zh || item.title}
                    </div>
                    <div className="mt-4 grid gap-2">
                      <InfoRow
                        label="价格"
                        value={item.current_price != null ? `${item.currency_code || ""} ${item.current_price}`.trim() : "待补充"}
                        tone="green"
                      />
                      <InfoRow label="评分" value={item.rating ? String(item.rating) : "待补充"} tone="blue" />
                      <InfoRow label="评论" value={item.review_count ? String(item.review_count) : "0"} tone="neutral" />
                    </div>
                  </Link>
                ))}
              </div>
            ) : (
              <EmptyState text="当前还没有真实商品进入首页推荐，先从采集或任务入口补充商品。" />
            )}
          </CardContent>
        </Card>

        <Card className="border-white/6 bg-[#111A2E]">
          <CardHeader>
            <CardTitle>今天应该怎么推进</CardTitle>
            <CardDescription>这块回答的是：如果你现在就在做 Shopify 店铺，今天先做哪一步最合适。</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-4">
            <ActionGuideCard
              icon={<TrendingUp className="h-4 w-4" />}
              title="先看市场"
              desc="如果你还没决定做什么商品，先去市场分析页看关键词和类目趋势。"
              href={ROUTES.insights}
              label="进入市场分析"
            />
            <ActionGuideCard
              icon={<ShoppingBag className="h-4 w-4" />}
              title="再定商品"
              desc="如果你已经有类目方向，比如家电，就去商品机会页筛更值得做的单品。"
              href={ROUTES.insightsOpportunities}
              label="进入商品机会"
            />
            <ActionGuideCard
              icon={<PackageSearch className="h-4 w-4" />}
              title="再匹配货源"
              desc="单品有机会后，再去供应链页看 1688 价格、评分、MOQ 和发货周期。"
              href={ROUTES.actionSuppliers}
              label="进入供应链匹配"
            />
            <ActionGuideCard
              icon={<ShieldAlert className="h-4 w-4" />}
              title="最后做利润和风险判断"
              desc="等市场、商品、货源都过了一轮，再去利润页和执行页，决定测试还是推进。"
              href={ROUTES.actionProfit}
              label="进入利润决策"
            />
          </CardContent>
        </Card>
      </section>

      <Card className="border-white/6 bg-[#111A2E]">
        <CardHeader>
          <CardTitle>今天推荐关注的类目</CardTitle>
          <CardDescription>先看大方向，再决定要不要继续深挖某个商品。</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4 xl:grid-cols-4">
          {categoryCards.length ? categoryCards.slice(0, 4).map((item, index) => (
            <Link
              key={`${item.name}-${index}`}
              href={`${ROUTES.insightsOpportunities}?category=${encodeURIComponent(item.name)}`}
              className="group rounded-2xl border border-white/6 bg-[rgba(255,255,255,0.02)] p-4 transition hover:-translate-y-0.5 hover:border-[#4F7CFF]/30 hover:bg-[rgba(79,124,255,0.06)]"
            >
              <div className="inline-flex rounded-full bg-[#4F7CFF]/12 px-3 py-1 text-xs font-semibold text-[#9CC0FF]">
                推荐类目 {index + 1}
              </div>
              <div className="mt-4 text-lg font-semibold text-white">{item.name}</div>
              <p className="mt-2 min-h-[72px] text-sm leading-7 text-white/60">
                当前系统里这个类目的入库商品数是 {item.product_count}，说明它现在更值得先点进去看。
              </p>
              <div className="mt-4 inline-flex items-center text-sm font-medium text-[#9CC0FF]">
                进入商品机会页
                <ArrowRight className="ml-2 h-4 w-4 transition group-hover:translate-x-0.5" />
              </div>
            </Link>
          )) : (
            <EmptyState text="现在还没有足够的类目推荐数据，先跑更多真实任务后，这里才会越来越像真正的机会首页。" />
          )}
        </CardContent>
      </Card>

      <section className="grid gap-6 xl:grid-cols-2">
        <Card className="border-white/6 bg-[#111A2E]">
          <CardHeader>
            <CardTitle>最近增长的商品方向</CardTitle>
            <CardDescription>这块回答的是：最近什么方向更值得继续看。</CardDescription>
          </CardHeader>
          <CardContent>
            {topRecommendations.length ? (
              <div className="grid gap-4 sm:grid-cols-2">
                {topRecommendations.slice(0, 4).map((item) => (
                  <Link
                    key={`${item.product_id}-${item.keyword}`}
                    href={productDetailRoute(item.product_id)}
                    className="group rounded-2xl border border-white/6 bg-[rgba(255,255,255,0.02)] p-4 transition hover:-translate-y-0.5 hover:border-[#4F7CFF]/30 hover:bg-[rgba(79,124,255,0.06)]"
                  >
                    <div className="flex items-center justify-between gap-2">
                      <Badge variant="brand" className="px-3 py-1.5 text-xs">
                        增长方向
                      </Badge>
                      <span className="text-xs text-white/45">{Math.round(item.recommendation_score)}/100</span>
                    </div>
                    <div className="mt-4 line-clamp-2 min-h-[44px] text-sm font-medium leading-6 text-white">
                      {item.title_zh || item.title}
                    </div>
                    <div className="mt-4 grid gap-2">
                      <InfoRow label={text.keyword} value={item.keyword} tone="neutral" />
                      <InfoRow label={text.profit} value={String(item.estimated_profit)} tone="green" />
                      <InfoRow label={text.suggestion} value={item.recommendation} tone="blue" />
                    </div>
                  </Link>
                ))}
              </div>
            ) : (
              <EmptyState text={text.noToday} />
            )}
          </CardContent>
        </Card>

        <Card className="border-white/6 bg-[#111A2E]">
          <CardHeader>
            <CardTitle>低竞争机会</CardTitle>
            <CardDescription>这块回答的是：哪些方向现在更可能切进去。</CardDescription>
          </CardHeader>
          <CardContent>
            {marketOpportunities.length ? (
              <div className="grid gap-4">
                {marketOpportunities.map((item, index) => (
                  <div key={`${item.product_id}-${index}`} className="rounded-2xl border border-white/6 bg-[rgba(255,255,255,0.02)] p-4">
                    <div className="flex items-center justify-between gap-2">
                      <div className="text-sm font-medium text-white">机会 {index + 1}</div>
                      <Badge variant={item.score >= 80 ? "success" : item.score >= 60 ? "warning" : "neutral"} className="px-3 py-1.5 text-xs">
                        {Math.round(item.score)}
                      </Badge>
                    </div>
                    <div className="mt-4 text-base font-semibold text-white">{item.title}</div>
                    <div className="mt-2 text-sm text-white/55">类目：{item.category || text.uncategorized}</div>
                    <div className="mt-4 grid gap-2">
                      <InfoRow label={text.heat} value={`${Math.round(item.score)}/100`} tone="orange" />
                      <InfoRow label={text.risk} value={item.score >= 80 ? text.riskLow : item.score >= 60 ? text.riskMid : text.riskHigh} tone={item.score >= 80 ? "green" : item.score >= 60 ? "orange" : "red"} />
                      <InfoRow label={text.profitRoom} value={item.score >= 80 ? text.roomHigh : item.score >= 60 ? text.roomWatch : text.roomCareful} tone={item.score >= 80 ? "green" : "blue"} />
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState text={text.noOpp} />
            )}
          </CardContent>
        </Card>
      </section>

      <Card className="border-white/6 bg-[#111A2E]">
        <CardHeader>
          <CardTitle>直接进入下一步</CardTitle>
          <CardDescription>你如果已经知道自己现在要看什么，就从这里直接跳过去。</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4 xl:grid-cols-4">
          {[
            {
              title: "进入类目市场页",
              desc: "先判断家电、美妆、宠物这些大类目是涨还是跌。",
              href: ROUTES.insightsCategories,
              label: "先看类目",
            },
            {
              title: "进入市场趋势页",
              desc: "看最近多少天是增长、持平还是下降。",
              href: ROUTES.insightsTrends,
              label: "先看趋势",
            },
            {
              title: "进入商品判断",
              desc: "你已经选定商品时，比如炒锅，就直接去做单品判断。",
              href: ROUTES.createTask,
              label: "看商品机会",
            },
            {
              title: "进入供应链匹配",
              desc: "判断完商品，再去看 1688 等供货结果。",
              href: ROUTES.actionSuppliers,
              label: "看1688匹配",
            },
          ].map((item) => (
            <Link
              key={item.title}
              href={item.href}
              className="rounded-2xl border border-white/6 bg-[rgba(255,255,255,0.02)] p-4 transition hover:-translate-y-0.5 hover:border-[#4F7CFF]/30 hover:bg-[rgba(79,124,255,0.06)]"
            >
              <div className="text-lg font-semibold text-white">{item.title}</div>
              <div className="mt-2 min-h-[72px] text-sm leading-7 text-white/60">{item.desc}</div>
              <div className="mt-4 inline-flex items-center text-sm font-medium text-[#9CC0FF]">
                {item.label}
                <ArrowRight className="ml-2 h-4 w-4" />
              </div>
            </Link>
          ))}
        </CardContent>
      </Card>

      <PlanAccessPanel currentPlan={currentPlan} title="你当前套餐能用哪些 AI 能力" />

      <section className="grid gap-4 xl:grid-cols-4">
        <MetricCard
          title={text.totalProducts}
          value={String(products.total)}
          description={text.totalProductsDesc}
          tone="blue"
          icon={<ShoppingBag className="h-5 w-5" />}
        />
        <MetricCard
          title={text.profitChance}
          value={String(totalProfit)}
          description={text.profitChanceDesc}
          tone="green"
          icon={<TrendingUp className="h-5 w-5" />}
        />
        <MetricCard
          title={text.marketHeat}
          value={`${avgMarketHeat}/100`}
          description={text.marketHeatDesc}
          tone="orange"
          icon={<Flame className="h-5 w-5" />}
        />
        <MetricCard
          title={text.aiIndex}
          value={`${avgAiScore}/100`}
          description={text.aiIndexDesc}
          tone="blue"
          icon={<Sparkles className="h-5 w-5" />}
        />
      </section>

      <section className="grid gap-6 xl:grid-cols-3">
        <Card className="border-white/6 bg-[#111A2E] xl:col-span-2">
          <CardHeader>
            <CardTitle>你现在可以直接做的事</CardTitle>
            <CardDescription>这块只讲你现在打开系统后，马上可以用起来的动作。</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-3 md:grid-cols-2">
            {[
              "先用市场页判断一个类目或者一个词是不是在增长。",
              "再用商品机会页继续筛出更值得做的具体商品。",
              "再去供应链页比 1688 价格、评分、MOQ 和发货周期。",
              "最后到利润页做判断，再决定要不要推进到上架。",
            ].map((item) => (
              <div key={item} className="rounded-2xl border border-white/6 bg-white/[0.03] p-4 text-sm leading-7 text-white/68">
                {item}
              </div>
            ))}
          </CardContent>
        </Card>

        <Card className="border-white/6 bg-[#111A2E]">
          <CardHeader>
            <CardTitle>常用入口</CardTitle>
            <CardDescription>你不想绕路时，就从这里直接进去。</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {[
              { label: "进入任务中心", href: ROUTES.tasks },
              { label: "进入账户中心", href: ROUTES.settings },
              { label: "进入套餐充值页", href: ROUTES.pricing },
              ...(isAdmin ? [{ label: "进入内部管理页", href: ROUTES.systemAdmin }] : []),
            ].map((item) => (
              <Link
                key={item.label}
                href={item.href}
                className="flex items-center justify-between rounded-2xl border border-white/6 bg-white/[0.03] px-4 py-3 text-sm text-white/75 transition hover:border-[#4F7CFF]/30 hover:bg-[rgba(79,124,255,0.06)]"
              >
                <span>{item.label}</span>
                <ArrowRight className="h-4 w-4 text-[#9CC0FF]" />
              </Link>
            ))}
          </CardContent>
        </Card>
      </section>

      <Card className="border-white/6 bg-[#111A2E]">
        <CardHeader>
          <CardTitle>最近分析记录</CardTitle>
          <CardDescription>这块展示最近真实跑过的分析记录，方便你接着往下看。</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4 xl:grid-cols-3">
          {latestRuns.length ? latestRuns.map((item) => (
            <div key={item.id} className="rounded-2xl border border-white/6 bg-white/[0.03] p-4">
              <div className="flex items-center justify-between gap-3">
                <div className="text-sm font-medium text-white">{item.platform_name}</div>
                <div className={`text-sm font-medium ${runStatusTone(item.status)}`}>{runStatusText(item.status)}</div>
              </div>
              <div className="mt-3 text-sm leading-6 text-white/55">这是你最近真实跑过的一条分析来源记录。</div>
              <div className="mt-3 break-all text-xs text-white/38">{item.request_url}</div>
              <div className="mt-3 text-xs text-white/38">{formatTimeText(item.crawled_at)}</div>
            </div>
          )) : (
            <div className="xl:col-span-3">
              <EmptyState text="现在还没有最近分析记录，你先跑一轮真实分析，这里才会逐步变成真正有用的经营首页。" />
            </div>
          )}
        </CardContent>
      </Card>

    </div>
  );
}

function StatusMetric({
  label,
  value,
  desc,
  tone,
}: {
  label: string;
  value: string;
  desc: string;
  tone: "green" | "orange" | "red" | "neutral";
}) {
  const toneMap = {
    green: "border-emerald-500/20 bg-emerald-500/10 text-emerald-300",
    orange: "border-amber-500/20 bg-amber-500/10 text-amber-300",
    red: "border-rose-500/20 bg-rose-500/10 text-rose-300",
    neutral: "border-white/8 bg-white/5 text-white",
  } as const;

  return (
    <div className={`rounded-2xl border p-4 ${toneMap[tone]}`}>
      <div className="text-xs uppercase tracking-[0.18em] text-white/45">{label}</div>
      <div className="mt-2 text-2xl font-semibold">{value}</div>
      <div className="mt-2 text-sm text-white/60">{desc}</div>
    </div>
  );
}

function QuickEntry({
  title,
  desc,
  href,
  label,
  icon,
}: {
  title: string;
  desc: string;
  href: string;
  label: string;
  icon?: React.ReactNode;
}) {
  return (
    <Link
      href={href}
      className="rounded-2xl border border-white/6 bg-[rgba(255,255,255,0.02)] p-4 transition hover:-translate-y-0.5 hover:border-[#4F7CFF]/30 hover:bg-[rgba(79,124,255,0.06)]"
    >
      {icon ? (
        <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-[#4F7CFF]/12 text-[#9CC0FF]">
          {icon}
        </div>
      ) : null}
      <div className="text-base font-semibold text-white">{title}</div>
      <div className="mt-2 min-h-[48px] text-sm leading-7 text-white/60">{desc}</div>
      <div className="mt-4 inline-flex items-center text-sm font-medium text-[#9CC0FF]">
        {label}
        <ArrowRight className="ml-2 h-4 w-4" />
      </div>
    </Link>
  );
}

function ActionGuideCard({
  icon,
  title,
  desc,
  href,
  label,
}: {
  icon: React.ReactNode;
  title: string;
  desc: string;
  href: string;
  label: string;
}) {
  return (
    <Link
      href={href}
      className="rounded-2xl border border-white/6 bg-[rgba(255,255,255,0.02)] p-4 transition hover:-translate-y-0.5 hover:border-[#4F7CFF]/30 hover:bg-[rgba(79,124,255,0.06)]"
    >
      <div className="flex items-start gap-3">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-white/6 text-[#9CC0FF]">
          {icon}
        </div>
        <div className="min-w-0">
          <div className="text-base font-semibold text-white">{title}</div>
          <div className="mt-2 text-sm leading-7 text-white/60">{desc}</div>
          <div className="mt-4 inline-flex items-center text-sm font-medium text-[#9CC0FF]">
            {label}
            <ArrowRight className="ml-2 h-4 w-4" />
          </div>
        </div>
      </div>
    </Link>
  );
}

function StageEntryCard({
  title,
  desc,
  href,
  label,
  badge,
}: {
  title: string;
  desc: string;
  href: string;
  label: string;
  badge: string;
}) {
  return (
    <Link
      href={href}
      className="rounded-2xl border border-white/6 bg-[#111A2E] p-5 transition hover:-translate-y-0.5 hover:border-[#4F7CFF]/30 hover:bg-[rgba(79,124,255,0.06)]"
    >
      <div className="inline-flex rounded-full bg-[#4F7CFF]/12 px-3 py-1 text-xs font-semibold text-[#9CC0FF]">
        {badge}
      </div>
      <div className="mt-4 text-lg font-semibold text-white">{title}</div>
      <div className="mt-3 min-h-[72px] text-sm leading-7 text-white/60">{desc}</div>
      <div className="mt-4 inline-flex items-center text-sm font-medium text-[#9CC0FF]">
        {label}
        <ArrowRight className="ml-2 h-4 w-4" />
      </div>
    </Link>
  );
}

function MetricCard({
  title,
  value,
  description,
  icon,
  tone,
}: {
  title: string;
  value: string;
  description: string;
  icon: React.ReactNode;
  tone: "blue" | "green" | "orange";
}) {
  const toneClass = {
    blue: "bg-[#4F7CFF]/12 text-[#4F7CFF]",
    green: "bg-[#3DD68C]/12 text-[#3DD68C]",
    orange: "bg-[#FFB020]/12 text-[#FFB020]",
  }[tone];

  return (
    <Card className="border-white/6 bg-[#111A2E]">
      <CardContent className="p-5">
        <div className="flex items-start justify-between gap-3">
          <div>
            <div className="text-sm text-white/52">{title}</div>
            <div className="mt-3 text-3xl font-semibold text-white">{value}</div>
            <div className="mt-2 text-sm leading-6 text-white/42">{description}</div>
          </div>
          <div className={`flex h-11 w-11 items-center justify-center rounded-2xl ${toneClass}`}>{icon}</div>
        </div>
      </CardContent>
    </Card>
  );
}

function InfoRow({
  label,
  value,
  tone,
}: {
  label: string;
  value: string;
  tone: "green" | "orange" | "red" | "blue" | "neutral";
}) {
  const toneClass = {
    green: "text-[#3DD68C]",
    orange: "text-[#FFB020]",
    red: "text-[#FF5C5C]",
    blue: "text-[#4F7CFF]",
    neutral: "text-white/75",
  }[tone];

  return (
    <div className="flex items-center justify-between gap-3 rounded-xl border border-white/6 bg-black/10 px-3 py-2.5">
      <span className="text-sm text-white/46">{label}</span>
      <span className={`text-sm font-medium ${toneClass}`}>{value}</span>
    </div>
  );
}

function taskStatusText(status: string) {
  if (status === "success") return "正常";
  if (status === "running") return "进行中";
  if (status === "pending") return "待开始";
  if (status === "blocked") return "已拦截";
  if (status === "error") return "异常";
  return "未知";
}

function taskStatusTone(status: string) {
  if (status === "success") return "text-[#3DD68C]";
  if (status === "running") return "text-[#4F7CFF]";
  if (status === "pending") return "text-[#FFB020]";
  if (status === "blocked" || status === "error") return "text-[#FF5C5C]";
  return "text-white/60";
}

function sourceHealthText(health: string) {
  if (health === "ok") return "正常";
  if (health === "warning") return "注意";
  if (health === "error") return "异常";
  return "未知";
}

function sourceHealthTone(health: string) {
  if (health === "ok") return "text-[#3DD68C]";
  if (health === "warning") return "text-[#FFB020]";
  if (health === "error") return "text-[#FF5C5C]";
  return "text-white/60";
}

function runStatusText(status: string) {
  if (status === "success") return "成功";
  if (status === "running") return "进行中";
  if (status === "failed" || status === "error") return "失败";
  return status || "未知";
}

function runStatusTone(status: string) {
  if (status === "success") return "text-[#3DD68C]";
  if (status === "running") return "text-[#4F7CFF]";
  if (status === "failed" || status === "error") return "text-[#FF5C5C]";
  return "text-white/60";
}

function formatTimeText(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return `最近时间：${date.toLocaleString("zh-CN", { hour12: false })}`;
}
