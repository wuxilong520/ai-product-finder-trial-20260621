"use client";

import { useEffect, useState } from "react";
import { Loader2, ShieldCheck } from "lucide-react";

import { recommendBusinessTruth } from "@/lib/api-gateway";
import { getToken } from "@/lib/auth";
import { Language, t } from "@/lib/i18n";
import type { BusinessTruthRecommendResponse } from "@/lib/types";
import { Badge, Card, CardContent, CardHeader, CardTitle, EmptyState, InfoTile, StatusBadge } from "@/design-system/components";

export function BusinessTruthCard({ productId, lang }: { productId: number; lang: Language }) {
  const text = t(lang);
  const [data, setData] = useState<BusinessTruthRecommendResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError("");
      try {
        const result = await recommendBusinessTruth(productId, getToken());
        if (!cancelled) {
          setData(result);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "商业真实性评分失败");
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
          <CardTitle>利润分析面板</CardTitle>
          <p className="mt-2 text-sm text-app-text-muted">基于真实售价、成本拆解和商业真实性增强层展示利润空间。</p>
        </div>
        <Badge variant="brand" className="px-4 py-2 text-sm font-medium">
          <ShieldCheck className="h-4 w-4" />
          Business Truth
        </Badge>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex items-center gap-2 text-sm text-app-text-secondary">
            <Loader2 className="h-4 w-4 animate-spin" />
            正在计算真实利润...
          </div>
        ) : error ? (
          <EmptyState text={error} />
        ) : data ? (
          <div className="space-y-5">
            <div className="flex flex-wrap gap-3">
              <Badge variant="brand" className="px-4 py-2 text-sm font-medium">
                商业评分 {Math.round(data.truth_score)} / 100
              </Badge>
              <StatusBadge status={data.truth_level === "A" ? "success" : data.truth_level === "B" ? "warning" : "blocked"} label={`${data.truth_level} 级`} />
              <StatusBadge status={data.profit_margin >= 0.2 ? "success" : data.profit_margin >= 0.1 ? "warning" : "blocked"} label={data.truth_recommendation} />
            </div>
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              <InfoTile label="预计利润" value={data.profit.toFixed(2)} />
              <InfoTile label="利润率" value={`${(data.profit_margin * 100).toFixed(1)}%`} />
              <InfoTile label="总成本" value={data.total_cost.toFixed(2)} />
              <InfoTile label="保本价" value={data.break_even_price.toFixed(2)} />
              <InfoTile label="真实市场价" value={data.real_market_price.toFixed(2)} />
              <InfoTile label="需求信号" value={data.demand_signal} />
            </div>
            <div className="rounded-2xl border border-app-border bg-white/5 p-4 shadow-app-soft">
              <p className="text-sm text-app-text-muted">利润判断说明</p>
              <div className="mt-3 space-y-2">
                {data.reasons.map((item) => (
                  <p key={item} className="text-sm text-app-text-secondary">
                    - {item}
                  </p>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <EmptyState text={text.emptyState} />
        )}
      </CardContent>
    </Card>
  );
}
