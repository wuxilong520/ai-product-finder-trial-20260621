"use client";

import { useEffect, useState } from "react";
import { CheckCircle2, Loader2, Rocket, Sparkles } from "lucide-react";

import { Badge, Button, Card, CardContent, CardHeader, CardTitle, EmptyState, InfoTile, StatusBadge } from "@/design-system/components";
import { getP5Recommendations } from "@/lib/api";
import { getToken } from "@/lib/auth";
import { Language, t } from "@/lib/i18n";
import type { P5RecommendationsResponse } from "@/lib/types";

export function OperationCenter({ lang }: { lang: Language }) {
  const text = t(lang);
  const flowSteps = [text.operationStep1, text.operationStep2, text.operationStep3, text.operationStep4];
  const [data, setData] = useState<P5RecommendationsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError("");
      try {
        const result = await getP5Recommendations({ limit: 5 }, getToken());
        if (!cancelled) setData(result);
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : text.operationLoadFailed);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    void load();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="space-y-5">
      <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
        <CardHeader>
          <div className="flex flex-wrap items-center gap-3">
            <Badge variant="brand"><Rocket className="h-4 w-4" />{text.navOperation}</Badge>
            <Badge variant="neutral"><Sparkles className="h-4 w-4" />{text.operationCoreFlow}</Badge>
          </div>
          <CardTitle>{text.operationTitle}</CardTitle>
          <p className="text-sm text-white/55">{text.operationDesc}</p>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-4">
          {flowSteps.map((step, index) => (
            <div key={step} className="rounded-2xl border border-white/8 bg-white/[0.03] p-4">
              <div className="text-xs uppercase tracking-[0.18em] text-white/35">Step {index + 1}</div>
              <div className="mt-2 text-sm font-medium text-white">{step}</div>
            </div>
          ))}
        </CardContent>
      </Card>

      {loading ? (
        <div className="flex min-h-[220px] items-center justify-center text-white/70"><Loader2 className="mr-2 h-5 w-5 animate-spin" />{text.operationLoading}</div>
      ) : error ? (
        <EmptyState text={error} />
      ) : data?.items.length ? (
        <div className="grid gap-4">
          {data.items.map((item) => (
            <Card key={item.product_id} className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
              <CardContent className="p-5">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <div className="text-base font-medium text-white">{item.title_zh || item.title}</div>
                    <div className="mt-1 text-sm text-white/45">{item.keyword}</div>
                  </div>
                  <StatusBadge status={item.recommendation_score >= 70 ? "success" : item.recommendation_score >= 50 ? "warning" : "blocked"} label={item.recommendation} />
                </div>
                <div className="mt-4 grid gap-4 md:grid-cols-3">
                  <InfoTile label={text.operationScore} value={`${Math.round(item.recommendation_score)} / 100`} />
                  <InfoTile label={text.operationProfit} value={String(item.estimated_profit)} />
                  <InfoTile label={text.operationCategory} value={item.category || text.operationPending} />
                </div>
                <div className="mt-4 flex flex-wrap gap-3">
                  <Button type="button">{text.operationConfirm}</Button>
                  <Button type="button" variant="outline">{text.operationObserve}</Button>
                  <Button type="button" variant="ghost"><CheckCircle2 className="mr-2 h-4 w-4" />{text.operationMarked}</Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <EmptyState text={text.operationEmpty} />
      )}
    </div>
  );
}
