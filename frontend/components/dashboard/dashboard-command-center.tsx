"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useMemo, useState } from "react";
import { ArrowRight, ChevronRight, Sparkles } from "lucide-react";

import { ROUTES, productDetailRoute } from "@/config/routes";
import { Badge, Button, Card, CardContent, EmptyState, InfoTile, Input, KpiTile } from "@/design-system/components";
import { homeHallCards, userPathCopy } from "@/lib/business-copy";
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
  const topRecommendations = recommendations?.items.slice(0, 6) || [];
  const hotCategories = summary.top_categories.slice(0, 6);
  const growthRanking = rankings?.growth_ranking.top_10.slice(0, 5) || [];
  const newestProducts = products.items.slice(0, 6);
  const activeSources = sources.sources.slice(0, 4);
  const totalProfit = topRecommendations.reduce((sum, item) => sum + Number(item.estimated_profit || 0), 0);
  const averageOpportunity = topRecommendations.length
    ? Math.round(topRecommendations.reduce((sum, item) => sum + item.recommendation_score, 0) / topRecommendations.length)
    : 0;
  const defaultKeyword = useMemo(() => {
    if (topRecommendations[0]?.keyword) return topRecommendations[0].keyword;
    if (growthRanking[0]?.title) return growthRanking[0].title;
    return "";
  }, [topRecommendations, growthRanking]);
  const [quickKeyword, setQuickKeyword] = useState(defaultKeyword);
  const pageText = lang === "en"
    ? {
        heroEyebrow: "Shanghang AI · Product Trend Hall",
        heroTitle: "See trend momentum first, then decide which products deserve your time.",
        heroDesc: "The homepage now works like a data product hall. It highlights trend direction, recommended products, profit room, and sourcing stability instead of looking like a backend panel.",
        heroPrimary: "View opportunity board",
        heroSecondary: "Start AI analysis",
        keywordPlaceholder: "Enter a product keyword to review",
        kpiOpportunity: "Today's opportunity signals",
        kpiProducts: "Board candidates",
        kpiProfit: "Projected profit room",
        kpiTasks: "Recent AI runs",
        pathTitle: "How to move through the product",
        boardTitle: "Recommended products today",
        boardEmpty: "No recommendation board yet. Add more real products first.",
        categoryTitle: "Fast-growing categories",
        categoryEmpty: "Not enough category data yet.",
        trendTitle: "Trend watchlist",
        trendEmpty: "Trend ranking is still building.",
        sourceTitle: "Current data sources",
        latestTitle: "Newest product additions",
        latestEmpty: "No real products in the library yet.",
      }
    : {
        heroEyebrow: "商航AI · 商品趋势大厅",
        heroTitle: "先看趋势和榜单，再决定哪些商品值得你花时间。",
        heroDesc: "首页现在是数据产品首页，不是后台。它会先告诉你趋势方向、推荐商品、利润空间和供应稳定性，让你 5 秒知道今天先看什么。",
        heroPrimary: "查看机会榜单",
        heroSecondary: "开始 AI 分析",
        keywordPlaceholder: "输入你想判断的商品关键词",
        kpiOpportunity: "今日市场机会",
        kpiProducts: "候选商品",
        kpiProfit: "利润空间预测",
        kpiTasks: "最近 AI 分析",
        pathTitle: "用户最顺手的使用路径",
        boardTitle: "今天优先看的推荐商品",
        boardEmpty: "现在还没有推荐榜单，先补充真实商品数据。",
        categoryTitle: "增长更快的类目",
        categoryEmpty: "当前类目数据还不够。",
        trendTitle: "值得盯住的趋势方向",
        trendEmpty: "趋势榜单还在形成中。",
        sourceTitle: "当前真实数据来源",
        latestTitle: "最新进入系统的商品",
        latestEmpty: "当前商品库还没有真实商品。",
      };

  function openInsights() {
    const keyword = quickKeyword.trim();
    router.push(keyword ? `${ROUTES.insights}?keyword=${encodeURIComponent(keyword)}` : ROUTES.insights);
  }

  function openCreate() {
    const keyword = quickKeyword.trim();
    router.push(keyword ? `${ROUTES.createTask}?keyword=${encodeURIComponent(keyword)}` : ROUTES.createTask);
  }

  return (
    <div className="space-y-6">
      <Card className="overflow-hidden border-white/8 bg-[linear-gradient(135deg,rgba(79,124,255,0.18),rgba(11,18,32,0.96))] shadow-[0_24px_60px_rgba(0,0,0,0.26)]">
        <CardContent className="grid gap-8 p-7 xl:grid-cols-[1.15fr_0.85fr]">
          <div className="space-y-6">
            <div>
              <div className="text-xs uppercase tracking-[0.24em] text-[#9CC0FF]">{pageText.heroEyebrow}</div>
              <h1 className="mt-3 max-w-4xl text-3xl font-semibold tracking-tight text-white md:text-4xl">
                {pageText.heroTitle}
              </h1>
              <p className="mt-4 max-w-3xl text-sm leading-8 text-white/66">{pageText.heroDesc}</p>
            </div>

            <div className="flex flex-col gap-3 rounded-[28px] border border-white/10 bg-black/10 p-4">
              <div className="text-sm font-medium text-white">一句话开始判断</div>
              <div className="flex flex-col gap-3 xl:flex-row">
                <Input
                  value={quickKeyword}
                  onChange={(event) => setQuickKeyword(event.target.value)}
                  placeholder={pageText.keywordPlaceholder}
                  className="xl:max-w-md"
                />
                <div className="flex flex-wrap gap-3">
                  <Button type="button" onClick={openInsights}>
                    {pageText.heroPrimary}
                  </Button>
                  <Button type="button" variant="secondary" onClick={openCreate}>
                    {pageText.heroSecondary}
                  </Button>
                </div>
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-4">
              <KpiTile label={pageText.kpiOpportunity} value={`${growthRanking.length} 个`} hint="今天值得先看的趋势方向" />
              <KpiTile label={pageText.kpiProducts} value={`${topRecommendations.length} 个`} hint="今天榜单里优先商品数量" />
              <KpiTile label={pageText.kpiProfit} value={totalProfit > 0 ? `¥${totalProfit.toFixed(2)}` : "待形成"} hint="基于当前榜单的利润空间汇总" />
              <KpiTile label={pageText.kpiTasks} value={`${tasks.recent_runs.length} 次`} hint="最近真实执行过的分析次数" />
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            {homeHallCards.map((card) => {
              const Icon = card.icon;
              const toneClass = toneStyle(card.tone);
              return (
                <div key={card.title} className="rounded-[28px] border border-white/10 bg-white/[0.05] p-5 shadow-[0_16px_32px_rgba(2,6,23,0.20)]">
                  <div className={`flex h-12 w-12 items-center justify-center rounded-2xl ${toneClass}`}>
                    <Icon className="h-5 w-5" />
                  </div>
                  <div className="mt-4 flex items-center justify-between gap-3">
                    <div className="text-base font-semibold text-white">{card.title}</div>
                    <Badge variant="neutral">{card.badge}</Badge>
                  </div>
                  <div className="mt-2 text-sm leading-7 text-white/60">{card.description}</div>
                  <div className="mt-4 text-sm font-medium text-white/78">{card.metric}</div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      <section className="grid gap-4 xl:grid-cols-[1.3fr_0.7fr]">
        <Card className="border-white/8 bg-[#111A2E]">
          <CardContent className="p-6">
            <div className="flex items-center justify-between gap-3">
              <div>
                <div className="text-lg font-semibold text-white">{pageText.boardTitle}</div>
                <div className="mt-2 text-sm text-white/55">优先展示真实商品推荐，不堆技术字段。</div>
              </div>
              <div className="rounded-full bg-[#4F7CFF]/10 px-4 py-2 text-sm text-[#9CC0FF]">
                平均机会指数 {averageOpportunity || 0}
              </div>
            </div>

            {topRecommendations.length ? (
              <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                {topRecommendations.map((item, index) => (
                  <Link
                    key={`${item.product_id}-${index}`}
                    href={productDetailRoute(item.product_id)}
                    className="rounded-[24px] border border-white/8 bg-white/[0.05] p-4 transition hover:-translate-y-0.5 hover:border-white/16 hover:bg-white/[0.07]"
                  >
                    <div className="flex items-center justify-between gap-3">
                      <span className="rounded-full bg-[#4F7CFF]/12 px-3 py-1 text-xs font-semibold text-[#9CC0FF]">TOP {index + 1}</span>
                      <span className="text-sm font-semibold text-white">{Math.round(item.recommendation_score)}</span>
                    </div>
                    <div className="mt-4 text-base font-semibold text-white">{item.title_zh || item.title}</div>
                    <div className="mt-2 text-sm text-white/48">{item.keyword}</div>
                    <div className="mt-4 grid gap-2">
                      <InfoTile label="市场机会指数" value={`${Math.round(item.recommendation_score)}/100`} />
                      <InfoTile label="利润空间预测" value={String(item.estimated_profit)} />
                      <InfoTile label="AI进入建议" value={item.recommendation} />
                    </div>
                    <div className="mt-4 text-sm leading-7 text-white/60">
                      {(item.reasons || []).slice(0, 2).map((reason) => `• ${reason}`).join(" ")}
                    </div>
                  </Link>
                ))}
              </div>
            ) : (
              <div className="mt-5">
                <EmptyState text={pageText.boardEmpty} />
              </div>
            )}
          </CardContent>
        </Card>

        <div className="space-y-4">
          <Card className="border-white/8 bg-[#111A2E]">
            <CardContent className="p-6">
              <div className="text-lg font-semibold text-white">{pageText.pathTitle}</div>
              <div className="mt-4 space-y-3">
                {userPathCopy.map((item, index) => {
                  const Icon = item.icon;
                  return (
                    <div key={item.title} className="flex items-start gap-3 rounded-2xl border border-white/8 bg-white/[0.04] p-4">
                      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-[#4F7CFF]/12 text-[#9CC0FF]">
                        <Icon className="h-4 w-4" />
                      </div>
                      <div className="min-w-0">
                        <div className="text-xs uppercase tracking-[0.18em] text-white/34">Step {index + 1}</div>
                        <div className="mt-1 text-sm font-semibold text-white">{item.title}</div>
                        <div className="mt-1 text-sm leading-7 text-white/58">{item.desc}</div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>

          <Card className="border-white/8 bg-[#111A2E]">
            <CardContent className="p-6">
              <div className="flex items-center justify-between gap-3">
                <div className="text-lg font-semibold text-white">{pageText.sourceTitle}</div>
                {currentPlan ? (
                  <Badge variant="neutral">{currentPlan.plan_name || "当前套餐"}</Badge>
                ) : null}
              </div>
              <div className="mt-4 space-y-3">
                {activeSources.length ? activeSources.map((item) => (
                  <div key={item.platform_code} className="flex items-center justify-between gap-3 rounded-2xl border border-white/8 bg-white/[0.04] px-4 py-3">
                    <div>
                      <div className="text-sm font-medium text-white">{item.platform_name}</div>
                      <div className="mt-1 text-xs text-white/45">{item.last_activity_text}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-white">{item.product_count}</div>
                      <div className="mt-1 text-xs text-white/45">{item.health}</div>
                    </div>
                  </div>
                )) : (
                  <EmptyState text="当前还没有可展示的数据来源。" />
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      <section className="grid gap-4 xl:grid-cols-2">
        <Card className="border-white/8 bg-[#111A2E]">
          <CardContent className="p-6">
            <div className="flex items-center justify-between gap-3">
              <div className="text-lg font-semibold text-white">{pageText.categoryTitle}</div>
              <Link href={ROUTES.insightsCategories} className="inline-flex items-center text-sm text-[#9CC0FF]">
                查看更多
                <ChevronRight className="ml-1 h-4 w-4" />
              </Link>
            </div>
            {hotCategories.length ? (
              <div className="mt-4 grid gap-3 md:grid-cols-2">
                {hotCategories.map((item) => (
                  <div key={item.name} className="rounded-2xl border border-white/8 bg-white/[0.04] p-4">
                    <div className="text-sm font-semibold text-white">{item.name}</div>
                    <div className="mt-2 text-sm text-white/55">当前商品数 {item.product_count}</div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="mt-4">
                <EmptyState text={pageText.categoryEmpty} />
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="border-white/8 bg-[#111A2E]">
          <CardContent className="p-6">
            <div className="flex items-center justify-between gap-3">
              <div className="text-lg font-semibold text-white">{pageText.trendTitle}</div>
              {isAdmin ? <Badge variant="neutral">管理员视角已开启</Badge> : null}
            </div>
            {growthRanking.length ? (
              <div className="mt-4 space-y-3">
                {growthRanking.map((item, index) => (
                  <div key={`${item.product_id}-${index}`} className="flex items-center justify-between gap-3 rounded-2xl border border-white/8 bg-white/[0.04] px-4 py-4">
                    <div className="min-w-0">
                      <div className="text-sm font-semibold text-white">{item.title}</div>
                      <div className="mt-1 text-xs text-white/45">{item.category || "未分类"}</div>
                    </div>
                    <div className="shrink-0 text-right">
                      <div className="text-sm font-semibold text-[#9CC0FF]">{Math.round(item.score)}</div>
                      <div className="mt-1 text-xs text-white/45">趋势热度</div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="mt-4">
                <EmptyState text={pageText.trendEmpty} />
              </div>
            )}
          </CardContent>
        </Card>
      </section>

      <Card className="border-white/8 bg-[#111A2E]">
        <CardContent className="p-6">
          <div className="flex items-center justify-between gap-3">
            <div className="text-lg font-semibold text-white">{pageText.latestTitle}</div>
            <Link href={ROUTES.products} className="inline-flex items-center text-sm text-[#9CC0FF]">
              去商品榜单
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </div>
          {newestProducts.length ? (
            <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {newestProducts.map((item) => (
                <Link
                  key={item.id}
                  href={productDetailRoute(item.id)}
                  className="rounded-[24px] border border-white/8 bg-white/[0.04] p-4 transition hover:border-white/16 hover:bg-white/[0.06]"
                >
                  <div className="flex items-center justify-between gap-3">
                    <div className="min-w-0">
                      <div className="truncate text-base font-semibold text-white">{item.title_zh || item.title}</div>
                      <div className="mt-1 truncate text-sm text-white/48">{item.title}</div>
                    </div>
                    <Sparkles className="h-4 w-4 text-[#9CC0FF]" />
                  </div>
                  <div className="mt-4 grid gap-2">
                    <InfoTile label="当前价格" value={item.current_price == null ? "待补充" : `${item.currency_code || ""} ${item.current_price}`} />
                    <InfoTile label="用户反馈" value={item.rating == null ? "待补充" : String(item.rating)} />
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <div className="mt-4">
              <EmptyState text={pageText.latestEmpty} />
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function toneStyle(tone: "blue" | "emerald" | "amber" | "rose") {
  if (tone === "emerald") return "bg-emerald-400/12 text-emerald-200";
  if (tone === "amber") return "bg-amber-400/12 text-amber-200";
  if (tone === "rose") return "bg-rose-400/12 text-rose-200";
  return "bg-[#4F7CFF]/12 text-[#9CC0FF]";
}
