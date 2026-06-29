"use client";

import { useEffect, useState } from "react";
import { BrainCircuit, Loader2 } from "lucide-react";

import { Badge, StatusBadge } from "@/design-system/components";
import { getProductIntelligence } from "@/lib/api-gateway";
import { getToken } from "@/lib/auth";
import { Language, t } from "@/lib/i18n";
import type { ProductIntelligenceEngineResponse } from "@/lib/types";

export function ProductIntelligenceBadge({ productId, lang }: { productId: number; lang: Language }) {
  const text = t(lang);
  const [data, setData] = useState<ProductIntelligenceEngineResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError(false);
      try {
        const result = await getProductIntelligence(productId, getToken());
        if (!cancelled) {
          setData(result);
        }
      } catch {
        if (!cancelled) {
          setError(true);
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

  if (loading) {
    return (
      <Badge variant="neutral" className="px-3 py-1.5 text-xs text-app-text-secondary">
        <Loader2 className="h-3.5 w-3.5 animate-spin" />
        {text.productIntelComputing}
      </Badge>
    );
  }

  if (error || !data) {
    return (
      <Badge variant="warning" className="px-3 py-1.5 text-xs">
        {text.productIntelUnavailable}
      </Badge>
    );
  }

  return (
    <div className="flex flex-wrap gap-2">
      <Badge variant="brand" className="px-3 py-1.5 text-xs">
        <BrainCircuit className="h-3.5 w-3.5" />
        {text.productIntelScore} {Math.round(data.recommendation_score)}
      </Badge>
      <StatusBadge status={toStatus(data.recommendation)} label={toRecommendationLabel(data.recommendation, text)} />
    </div>
  );
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
