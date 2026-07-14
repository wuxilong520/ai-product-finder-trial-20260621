"use client";

import { useEffect, useState } from "react";
import { BrainCircuit, Loader2 } from "lucide-react";

import { Badge, Card, CardContent, CardHeader, CardTitle, EmptyState, InfoTile, StatusBadge } from "@/design-system/components";
import { getProductIntelligence } from "@/lib/api-gateway";
import { getToken } from "@/lib/auth";
import { Language, t } from "@/lib/i18n";
import type { ProductIntelligenceEngineResponse } from "@/lib/types";

export function ProductIntelligencePanel({ productId, lang }: { productId: number; lang: Language }) {
  const text = t(lang);
  const [data, setData] = useState<ProductIntelligenceEngineResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const reasons = Array.isArray(data?.reasons) ? data.reasons : [];

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const result = await getProductIntelligence(productId, getToken());
        if (!cancelled) {
          setData(result);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : text.productIntelEmpty);
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
  }, [productId]);

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle>{text.productIntelTitle}</CardTitle>
          <p className="mt-2 text-sm text-app-text-muted">{text.productIntelDesc}</p>
        </div>
        <Badge variant="brand" className="px-3 py-2 text-sm">
          <BrainCircuit className="h-4 w-4" />
          Phase 1
        </Badge>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex items-center gap-2 text-sm text-app-text-secondary">
            <Loader2 className="h-4 w-4 animate-spin" />
            {text.productIntelLoading}
          </div>
        ) : error ? (
          <EmptyState text={error} />
        ) : data ? (
          <div className="space-y-5">
            <div className="flex flex-wrap gap-3">
              <Badge variant="brand" className="px-4 py-2 text-sm font-medium">
                {text.productIntelScore} {Math.round(data.recommendation_score)} / 100
              </Badge>
              <StatusBadge status={toStatus(data.recommendation)} label={toRecommendationLabel(data.recommendation, text)} />
            </div>
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
              <InfoTile label={text.productIntelMarket} value={scoreText(data.market_score)} />
              <InfoTile label={text.productIntelCompetition} value={scoreText(data.competition_score)} />
              <InfoTile label={text.productIntelProfit} value={scoreText(data.profit_score)} />
              <InfoTile label={text.productIntelRisk} value={scoreText(data.risk_score)} />
              <InfoTile label={text.productIntelRecommend} value={scoreText(data.recommendation_score)} />
            </div>
              <div className="rounded-2xl border border-app-border bg-white/5 p-4 shadow-app-soft">
                <p className="text-sm text-app-text-muted">{text.productIntelReasons}</p>
                <div className="mt-3 space-y-2">
                  {reasons.length ? reasons.map((item) => (
                    <p key={item} className="text-sm text-app-text-secondary">
                      - {item}
                    </p>
                  )) : <p className="text-sm text-app-text-secondary">- {text.emptyState}</p>}
                </div>
              </div>
            </div>
        ) : (
          <EmptyState text={text.productIntelEmpty} />
        )}
      </CardContent>
    </Card>
  );
}

function scoreText(value: number) {
  return `${Math.round(value)} / 100`;
}

function toStatus(value: ProductIntelligenceEngineResponse["recommendation"]) {
  if (value === "推荐上架") return "success";
  if (value === "观察") return "warning";
  return "blocked";
}

function toRecommendationLabel(value: ProductIntelligenceEngineResponse["recommendation"], text: ReturnType<typeof t>) {
  if (value === "推荐上架") return text.productIntelRecommendReady;
  if (value === "观察") return text.productIntelRecommendWatch;
  return text.productIntelRecommendSkip;
}
