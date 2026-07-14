"use client";

import { useEffect, useState } from "react";
import { BrainCircuit, Loader2 } from "lucide-react";

import { Badge, Card, CardContent, CardHeader, CardTitle, EmptyState, InfoTile, StatusBadge } from "@/design-system/components";
import { recommendDecision } from "@/lib/api-gateway";
import { getToken } from "@/lib/auth";
import { Language, t } from "@/lib/i18n";
import type { DecisionRecommendResponse } from "@/lib/types";


export function DecisionCard({ productId, lang = "zh" }: { productId: number; lang?: Language }) {
  const text = t(lang);
  const [data, setData] = useState<DecisionRecommendResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const reasons = Array.isArray(data?.reasons) ? data.reasons : [];

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError("");
      try {
        const result = await recommendDecision(productId, getToken());
        if (!cancelled) {
          setData(result);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : text.decisionFailed);
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
      <CardHeader className="flex flex-row items-center justify-between gap-4">
        <div>
          <CardTitle>{text.decisionTitle}</CardTitle>
          <p className="mt-2 text-sm text-app-text-muted">{text.decisionDesc}</p>
        </div>
        <Badge variant="brand" className="px-4 py-2 text-sm font-medium">
          <BrainCircuit className="h-4 w-4" />
          {text.decisionBadge}
        </Badge>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex items-center gap-2 text-sm text-app-text-secondary">
            <Loader2 className="h-4 w-4 animate-spin" />
            {text.decisionLoading}
          </div>
        ) : error ? (
          <EmptyState text={error} />
        ) : data ? (
          <div className="space-y-5">
            <div className="flex flex-wrap gap-3">
              <Badge variant="brand" className="px-4 py-2 text-sm font-medium">{text.decisionFinalScore} {Math.round(data.final_score)} / 100</Badge>
              <StatusBadge status={toLevelStatus(data.recommendation_level)} label={`${data.recommendation_level} ${text.decisionLevel}`} />
              <StatusBadge status={toRecommendationStatus(data.recommendation)} label={toRecommendationLabel(data.recommendation, text)} />
            </div>
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              <InfoTile label={text.decisionIntelligence} value={scoreText(data.intelligence_score)} />
              <InfoTile label={text.decisionMarket} value={scoreText(data.market_score)} />
              <InfoTile label={text.decisionSupplier} value={scoreText(data.supplier_score)} />
              <InfoTile label={text.decisionProfit} value={scoreText(data.profit_score)} />
              <InfoTile label={text.decisionRisk} value={scoreText(data.risk_score)} />
              <InfoTile label={text.decisionFinal} value={scoreText(data.final_score)} />
            </div>
            <div className="rounded-2xl border border-app-border bg-white/5 p-4 shadow-app-soft">
              <p className="text-sm text-app-text-muted">{text.decisionReasons}</p>
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
          <EmptyState text={text.decisionEmpty} />
        )}
      </CardContent>
    </Card>
  );
}

function scoreText(value: number) {
  return `${Math.round(value)} / 100`;
}

function toLevelStatus(level: string) {
  if (level === "S" || level === "A") return "success";
  if (level === "B") return "warning";
  return "blocked";
}

function toRecommendationStatus(value: string) {
  if (value === "强烈推荐上架" || value === "推荐上架") return "success";
  if (value === "继续观察") return "warning";
  return "blocked";
}

function toRecommendationLabel(value: string, text: ReturnType<typeof t>) {
  if (value === "强烈推荐上架" || value === "推荐上架") return text.productIntelRecommendReady;
  if (value === "继续观察") return text.productIntelRecommendWatch;
  return text.productIntelRecommendSkip;
}
