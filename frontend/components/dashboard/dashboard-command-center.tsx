"use client";

import Link from "next/link";
import { ArrowRight, Flame, ShoppingBag, Sparkles, TrendingUp } from "lucide-react";

import { PlanAccessPanel } from "@/components/billing/plan-access-panel";
import { ROUTES, productDetailRoute } from "@/config/routes";
import { Badge, Card, CardContent, CardDescription, CardHeader, CardTitle, EmptyState, InfoTile } from "@/design-system/components";
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
  const totalProfit = topRecommendations.reduce((sum, item) => sum + Number(item.estimated_profit || 0), 0);
  const avgAiScore = topRecommendations.length
    ? Math.round(topRecommendations.reduce((sum, item) => sum + item.recommendation_score, 0) / topRecommendations.length)
    : 0;
  const avgMarketHeat = marketOpportunities.length
    ? Math.round(marketOpportunities.reduce((sum, item) => sum + item.score, 0) / marketOpportunities.length)
    : 0;

  return (
    <div className="space-y-6">
      <Card className="border-white/6 bg-[linear-gradient(135deg,rgba(79,124,255,0.16),rgba(17,26,46,0.95))]">
        <CardContent className="flex flex-col gap-6 p-6 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-3xl">
            <div className="text-xs uppercase tracking-[0.22em] text-[#D8E3FF]">商航AI · 产品功能首页</div>
            <h1 className="mt-3 text-3xl font-semibold tracking-tight text-white lg:text-4xl">
              先回答一件事：我今天该先看什么
            </h1>
            <p className="mt-3 text-sm leading-7 text-white/68">
              如果你现在在做 Shopify 店铺，首页不应该先把一堆任务状态丢给你。这里先把今天推荐关注的类目、最近增长的商品方向、低竞争机会和市场分析入口给你，让你先知道今天优先看什么。
            </p>
          </div>
          <div className="grid gap-3 sm:grid-cols-3 lg:min-w-[420px]">
            <InfoTile label="今天先看" value="类目和机会" />
            <InfoTile label="下一步" value="市场分析" />
            <InfoTile label="最终目标" value="找到能做的商品" />
          </div>
        </CardContent>
      </Card>

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
          <CardTitle>直接进入市场分析</CardTitle>
          <CardDescription>你如果已经确定类目，比如家电，就从这里继续往下走。</CardDescription>
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

      <PlanAccessPanel currentPlan={currentPlan} title="你当前这套账号能调用什么 AI" />

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

      {isAdmin ? (
        <Card className="border-white/6 bg-[#111A2E]">
          <CardContent className="flex flex-col gap-4 p-6 md:flex-row md:items-center md:justify-between">
            <div>
              <div className="text-xs uppercase tracking-[0.22em] text-white/35">商航AI · 内部运营入口</div>
              <div className="mt-2 text-xl font-semibold text-white">你当前账号拥有后台权限</div>
              <div className="mt-2 text-sm leading-7 text-white/60">
                可以直接进入内部管理后台，查看用户、收入和系统状态。
              </div>
            </div>
            <Link
              href={ROUTES.systemAdmin}
              className="inline-flex items-center justify-center rounded-full border border-white/10 bg-white/5 px-5 py-3 text-sm text-white transition hover:bg-white/10"
            >
              进入后台管理
            </Link>
          </CardContent>
        </Card>
      ) : null}

      <section className="grid gap-6 xl:grid-cols-2">
        <Card className="border-white/6 bg-[#111A2E]">
          <CardHeader>
            <CardTitle>补充看板：今日值得关注商品</CardTitle>
            <CardDescription>这块放在机会判断后面，不再抢首页第一眼。</CardDescription>
          </CardHeader>
          <CardContent>
            {topRecommendations.length ? (
              <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                {topRecommendations.slice(0, 8).map((item) => (
                  <Link
                    key={`${item.product_id}-${item.keyword}`}
                    href={productDetailRoute(item.product_id)}
                    className="group rounded-2xl border border-white/6 bg-[rgba(255,255,255,0.02)] p-4 transition hover:-translate-y-0.5 hover:border-[#4F7CFF]/30 hover:bg-[rgba(79,124,255,0.06)]"
                  >
                    <div className="flex items-center justify-between gap-2">
                      <Badge variant="brand" className="px-3 py-1.5 text-xs">
                        {text.recommendBadge}
                      </Badge>
                      <span className="text-xs text-white/45">{Math.round(item.recommendation_score)}/100</span>
                    </div>
                    <div className="mt-4 line-clamp-2 min-h-[44px] text-sm font-medium leading-6 text-white">
                      {item.title_zh || item.title}
                    </div>
                    <div className="mt-4 grid gap-2">
                      <InfoRow label={text.profit} value={String(item.estimated_profit)} tone="green" />
                      <InfoRow label={text.keyword} value={item.keyword} tone="neutral" />
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
            <CardTitle>补充看板：类目分布</CardTitle>
            <CardDescription>这是辅助信息，不再代替“今天先看什么”的主判断。</CardDescription>
          </CardHeader>
          <CardContent>
            {categoryCards.length ? (
              <div className="flex gap-4 overflow-x-auto pb-2">
                {categoryCards.map((item, index) => (
                  <div key={`${item.name}-${index}`} className="min-w-[220px] rounded-2xl border border-white/6 bg-[rgba(255,255,255,0.02)] p-4">
                    <div className="flex items-center justify-between gap-2">
                      <Badge variant="neutral" className="px-3 py-1.5 text-xs">
                        {text.categoryBadge}
                      </Badge>
                      <span className="text-xs text-white/40">TOP {index + 1}</span>
                    </div>
                    <div className="mt-4 text-base font-semibold text-white">{item.name}</div>
                    <div className="mt-3 text-sm text-white/55">{text.categoryCount}{item.product_count}</div>
                    <div className="mt-5 h-2 rounded-full bg-white/6">
                      <div
                        className="h-2 rounded-full bg-[linear-gradient(90deg,#4F7CFF,#3DD68C)]"
                        style={{ width: `${Math.min(100, item.product_count * 8)}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState text={text.noCategory} />
            )}
          </CardContent>
        </Card>
      </section>

      <section className="grid gap-6 xl:grid-cols-3">
        <Card className="border-white/6 bg-[#111A2E] xl:col-span-2">
          <CardHeader>
            <CardTitle>现在这套系统已经走到哪里</CardTitle>
            <CardDescription>这里只写当前页面和代码里已经收口到的东西，不写没做完的空话。</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-3 md:grid-cols-2">
            {[
              "登录后首页已经按产品入口聚合市场、商品、供应链、利润和执行入口。",
              "任务详情页已经能把市场智能层、1688 结果、利润和 Shopify 出口放一起看。",
              "套餐、账户、订单和封号提示都已经有独立页面承接。",
              "真实平台的最终自动发布还没完全收口，所以执行页现在还是以准备和队列为主。",
            ].map((item) => (
              <div key={item} className="rounded-2xl border border-white/6 bg-white/[0.03] p-4 text-sm leading-7 text-white/68">
                {item}
              </div>
            ))}
          </CardContent>
        </Card>

        <Card className="border-white/6 bg-[#111A2E]">
          <CardHeader>
            <CardTitle>快速入口</CardTitle>
            <CardDescription>把常用入口放在一起，少走弯路。</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {[
              { label: "进入任务中心", href: ROUTES.tasks },
              { label: "进入账户中心", href: ROUTES.settings },
              { label: "进入套餐充值页", href: ROUTES.pricing },
              { label: "查看产品健康页", href: ROUTES.productDashboard },
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

    </div>
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
