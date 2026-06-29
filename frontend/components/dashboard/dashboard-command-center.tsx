"use client";

import Link from "next/link";
import { Flame, ShoppingBag, Sparkles, TrendingUp } from "lucide-react";

import { ROUTES, productDetailRoute } from "@/config/routes";
import { Badge, Card, CardContent, CardDescription, CardHeader, CardTitle, EmptyState, InfoTile } from "@/design-system/components";
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
      <section className="grid gap-4 xl:grid-cols-4">
        <MetricCard
          title="总商品量"
          value={String(products.total)}
          description="当前进入系统的真实商品数量"
          tone="blue"
          icon={<ShoppingBag className="h-5 w-5" />}
        />
        <MetricCard
          title="利润机会"
          value={String(totalProfit)}
          description="推荐商品的累计预估利润"
          tone="green"
          icon={<TrendingUp className="h-5 w-5" />}
        />
        <MetricCard
          title="市场热度"
          value={`${avgMarketHeat}/100`}
          description="来自增长榜的综合热度"
          tone="orange"
          icon={<Flame className="h-5 w-5" />}
        />
        <MetricCard
          title="AI推荐指数"
          value={`${avgAiScore}/100`}
          description="当前推荐商品的平均决策分"
          tone="blue"
          icon={<Sparkles className="h-5 w-5" />}
        />
      </section>

      <section className="grid gap-6 xl:grid-cols-2">
        <Card className="border-white/6 bg-[#111A2E]">
          <CardHeader>
            <CardTitle>今日值得关注商品</CardTitle>
            <CardDescription>这里展示今天最值得优先关注的真实商品。</CardDescription>
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
                        推荐
                      </Badge>
                      <span className="text-xs text-white/45">{Math.round(item.recommendation_score)}/100</span>
                    </div>
                    <div className="mt-4 line-clamp-2 min-h-[44px] text-sm font-medium leading-6 text-white">
                      {item.title_zh || item.title}
                    </div>
                    <div className="mt-4 grid gap-2">
                      <InfoRow label="利润" value={String(item.estimated_profit)} tone="green" />
                      <InfoRow label="关键词" value={item.keyword} tone="neutral" />
                      <InfoRow label="建议" value={item.recommendation} tone="blue" />
                    </div>
                  </Link>
                ))}
              </div>
            ) : (
              <EmptyState text="现在还没有形成今日推荐商品，先从采集真实商品开始。" />
            )}
          </CardContent>
        </Card>

        <Card className="border-white/6 bg-[#111A2E]">
          <CardHeader>
            <CardTitle>热门增长类目</CardTitle>
            <CardDescription>用真实商品分布和增长结果，快速看当前更值得关注的类目方向。</CardDescription>
          </CardHeader>
          <CardContent>
            {categoryCards.length ? (
              <div className="flex gap-4 overflow-x-auto pb-2">
                {categoryCards.map((item, index) => (
                  <div key={`${item.name}-${index}`} className="min-w-[220px] rounded-2xl border border-white/6 bg-[rgba(255,255,255,0.02)] p-4">
                    <div className="flex items-center justify-between gap-2">
                      <Badge variant="neutral" className="px-3 py-1.5 text-xs">
                        类目
                      </Badge>
                      <span className="text-xs text-white/40">TOP {index + 1}</span>
                    </div>
                    <div className="mt-4 text-base font-semibold text-white">{item.name}</div>
                    <div className="mt-3 text-sm text-white/55">当前入库商品数：{item.product_count}</div>
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
              <EmptyState text="当前还没有足够类目分布数据。" />
            )}
          </CardContent>
        </Card>
      </section>

      <section className="grid gap-6 xl:grid-cols-3">
        <Card className="border-white/6 bg-[#111A2E] xl:col-span-3">
          <CardHeader>
            <CardTitle>潜力市场机会</CardTitle>
            <CardDescription>看现在更值得深入判断的机会方向。</CardDescription>
          </CardHeader>
          <CardContent>
            {marketOpportunities.length ? (
              <div className="grid gap-4 md:grid-cols-3">
                {marketOpportunities.map((item, index) => (
                  <div key={`${item.product_id}-${item.title}-${index}`} className="rounded-2xl border border-white/6 bg-[rgba(255,255,255,0.02)] p-5">
                    <div className="flex items-center justify-between gap-2">
                      <div className="text-sm font-medium text-white">机会 {index + 1}</div>
                      <Badge variant={item.score >= 80 ? "success" : item.score >= 60 ? "warning" : "neutral"} className="px-3 py-1.5 text-xs">
                        {Math.round(item.score)}
                      </Badge>
                    </div>
                    <div className="mt-4 line-clamp-2 min-h-[44px] text-base font-semibold leading-6 text-white">
                      {item.title}
                    </div>
                    <div className="mt-3 text-sm text-white/55">类目：{item.category || "未分类"}</div>
                    <div className="mt-4 grid gap-3">
                      <InfoRow label="热度" value={`${Math.round(item.score)}/100`} tone="orange" />
                      <InfoRow label="风险" value={item.score >= 80 ? "中低" : item.score >= 60 ? "中等" : "偏高"} tone={item.score >= 80 ? "green" : item.score >= 60 ? "orange" : "red"} />
                      <InfoRow label="利润空间" value={item.score >= 80 ? "较高" : item.score >= 60 ? "可观察" : "谨慎"} tone={item.score >= 80 ? "green" : "blue"} />
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState text="当前还没有形成清晰的市场机会结果。" />
            )}
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
