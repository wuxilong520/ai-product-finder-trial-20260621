"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { BarChart3, BrainCircuit, Loader2, Sparkles, TrendingUp, TriangleAlert } from "lucide-react";

import { Badge, Card, CardContent, CardHeader, CardTitle, EmptyState, InfoTile, StatusBadge } from "@/design-system/components";
import { getP5Rankings, predictP5Product } from "@/lib/api-gateway";
import { getToken } from "@/lib/auth";
import { Language, t } from "@/lib/i18n";
import type { P5PredictionResponse, P5RankingsResponse } from "@/lib/types";
import { productDetailRoute } from "@/config/routes";

export function P5Dashboard({ lang }: { lang: Language }) {
  const text = t(lang);
  const [rankings, setRankings] = useState<P5RankingsResponse | null>(null);
  const [prediction, setPrediction] = useState<P5PredictionResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError("");
      try {
        const rankingData = await getP5Rankings(getToken());
        if (cancelled) return;
        setRankings(rankingData);
        const topGrowth = rankingData.growth_ranking.top_10[0];
        if (topGrowth) {
          const predictionData = await predictP5Product(topGrowth.product_id, 30, getToken());
          if (!cancelled) {
            setPrediction(predictionData);
          }
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : text.p5LoadFailed);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }
    void load();
    return () => {
      cancelled = true;
    };
  }, []);

  if (loading) {
    return (
      <div className="flex min-h-[320px] items-center justify-center text-white/70">
        <Loader2 className="mr-2 h-5 w-5 animate-spin" />
        {text.p5Loading}
      </div>
    );
  }

  if (error) {
    return <EmptyState text={error} />;
  }

  if (!rankings) {
    return <EmptyState text={text.p5Empty} />;
  }

  return (
    <div className="space-y-6">
      <Card className="border-white/8 bg-[linear-gradient(180deg,rgba(255,255,255,0.04),rgba(255,255,255,0.02))] p-5 shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
        <div className="flex flex-wrap items-center gap-3">
          <Badge variant="brand" className="px-4 py-2 text-sm font-medium">
            <BrainCircuit className="h-4 w-4" />
            {text.p5Badge}
          </Badge>
          <Badge variant="neutral" className="px-4 py-2 text-sm text-app-text-secondary">
            <Sparkles className="h-4 w-4 text-app-brand-secondary" />
            {text.p5SystemName}
          </Badge>
        </div>
        <h1 className="mt-4 text-3xl font-semibold tracking-tight text-white">{text.p5Title}</h1>
        <p className="mt-2 max-w-3xl text-sm leading-7 text-white/60">
          {text.p5Desc}
        </p>
      </Card>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <InfoTile label={text.p5ScannedProducts} value={String(rankings.scanned_products)} />
        <InfoTile label={text.p5ProfitTop} value={String(rankings.profit_ranking.top_10.length)} />
        <InfoTile label={text.p5GrowthTop} value={String(rankings.growth_ranking.top_10.length)} />
        <InfoTile label={text.p5RiskTop} value={String(rankings.risk_ranking.top_10.length)} />
      </div>

      {prediction ? (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between gap-4">
            <div>
              <CardTitle>{text.p5PredictionTitle}</CardTitle>
              <p className="mt-2 text-sm text-app-text-muted">{text.p5PredictionDesc}</p>
            </div>
            <StatusBadge
              status={prediction.explosion_probability >= 70 ? "success" : prediction.explosion_probability >= 50 ? "warning" : "blocked"}
              label={`${text.p5ExplosionProbability} ${Math.round(prediction.explosion_probability)}`}
            />
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
              <InfoTile label={text.p5GrowthForecast} value={`${Math.round(prediction.growth_forecast)} / 100`} />
              <InfoTile label={text.p5DemandForecast} value={`${Math.round(prediction.demand_forecast)} / 100`} />
              <InfoTile label={text.p5CompetitionForecast} value={`${Math.round(prediction.competition_forecast)} / 100`} />
              <InfoTile label={text.p5ProfitForecast} value={`${Math.round(prediction.profit_forecast)} / 100`} />
              <InfoTile label={text.p5ExplosionProbability} value={`${Math.round(prediction.explosion_probability)} / 100`} />
            </div>
            <div className="rounded-2xl border border-app-border bg-white/5 p-4 shadow-app-soft">
              <p className="text-sm text-app-text-muted">{text.p5PredictionReason}</p>
              <div className="mt-3 space-y-2">
                {prediction.reasons.map((item) => (
                  <p key={item} className="text-sm text-app-text-secondary">
                    - {item}
                  </p>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      ) : null}

      <div className="grid gap-6 xl:grid-cols-3">
        <RankingCard
          title={text.p5ProfitRanking}
          icon={<BarChart3 className="h-4 w-4" />}
          items={rankings.profit_ranking.top_10}
          tone="success"
          emptyText={text.p5NoRanking}
          uncategorizedText={text.p5Uncategorized}
        />
        <RankingCard
          title={text.p5GrowthRanking}
          icon={<TrendingUp className="h-4 w-4" />}
          items={rankings.growth_ranking.top_10}
          tone="brand"
          emptyText={text.p5NoRanking}
          uncategorizedText={text.p5Uncategorized}
        />
        <RankingCard
          title={text.p5LowRiskRanking}
          icon={<TriangleAlert className="h-4 w-4" />}
          items={rankings.risk_ranking.top_10}
          tone="warning"
          reverseMeaning
          emptyText={text.p5NoRanking}
          uncategorizedText={text.p5Uncategorized}
        />
      </div>
    </div>
  );
}

function RankingCard({
  title,
  icon,
  items,
  tone,
  reverseMeaning = false,
  emptyText,
  uncategorizedText,
}: {
  title: string;
  icon: React.ReactNode;
  items: P5RankingsResponse["profit_ranking"]["top_10"];
  tone: "success" | "brand" | "warning";
  reverseMeaning?: boolean;
  emptyText: string;
  uncategorizedText: string;
}) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2 text-white">
          {icon}
          <CardTitle>{title}</CardTitle>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {items.length ? items.map((item, index) => (
            <Link
              key={`${title}-${item.product_id}`}
              href={productDetailRoute(item.product_id)}
              className="flex items-center justify-between rounded-2xl border border-app-border bg-white/4 px-4 py-3 transition hover:border-app-border-strong hover:bg-white/8"
            >
              <div className="min-w-0">
                <p className="text-sm text-app-text-muted">TOP {index + 1}</p>
                <p className="truncate text-sm font-medium text-white">{item.title}</p>
                <p className="text-xs text-app-text-muted">{item.category || uncategorizedText}</p>
              </div>
              <Badge variant={tone} className="px-3 py-1 text-sm">
                {reverseMeaning ? Math.round(item.score) : `${Math.round(item.score)}`}
              </Badge>
            </Link>
          )) : <EmptyState text={emptyText} />}
        </div>
      </CardContent>
    </Card>
  );
}
