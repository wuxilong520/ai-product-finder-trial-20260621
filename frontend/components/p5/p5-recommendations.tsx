"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Loader2, Search, Sparkles } from "lucide-react";

import { Badge, Button, Card, CardContent, CardHeader, CardTitle, EmptyState, Input, StatusBadge } from "@/design-system/components";
import { getP5Recommendations } from "@/lib/api-gateway";
import { getToken } from "@/lib/auth";
import { productDetailRoute } from "@/config/routes";
import { Language, t } from "@/lib/i18n";
import type { P5RecommendationsResponse } from "@/lib/types";

export function P5Recommendations({ lang }: { lang: Language }) {
  const text = t(lang);
  const [keyword, setKeyword] = useState("air fryer");
  const [category, setCategory] = useState("");
  const [data, setData] = useState<P5RecommendationsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function load(params?: { keyword?: string; category?: string }) {
    setLoading(true);
    setError("");
    try {
      const result = await getP5Recommendations({ keyword: params?.keyword ?? keyword, category: params?.category ?? category, limit: 10 }, getToken());
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : text.p5RecommendationLoadFailed);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="space-y-6">
      <Card className="border-white/8 bg-[linear-gradient(180deg,rgba(255,255,255,0.04),rgba(255,255,255,0.02))] p-5 shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
        <div className="flex flex-wrap items-center gap-3">
          <Badge variant="brand" className="px-4 py-2 text-sm font-medium">
            <Sparkles className="h-4 w-4" />
            {text.p5RecommendationMode}
          </Badge>
        </div>
        <h1 className="mt-4 text-3xl font-semibold tracking-tight text-white">{text.p5RecommendationTitle}</h1>
        <p className="mt-2 max-w-3xl text-sm leading-7 text-white/60">
          {text.p5RecommendationDesc}
        </p>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{text.p5RecommendationInput}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 md:grid-cols-[1fr_1fr_auto]">
            <div className="relative">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-app-text-muted" />
              <Input value={keyword} onChange={(event) => setKeyword(event.target.value)} placeholder={text.marketKeywordPlaceholder} className="pl-9" />
            </div>
            <Input value={category} onChange={(event) => setCategory(event.target.value)} placeholder={text.p5CategoryPlaceholder} />
            <Button type="button" onClick={() => void load()}>
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  {text.p5Generating}
                </>
              ) : (
                text.p5Generate
              )}
            </Button>
          </div>
          {error ? <div className="mt-4 rounded-2xl border border-rose-400/20 bg-rose-400/10 px-4 py-3 text-sm text-rose-200">{error}</div> : null}
        </CardContent>
      </Card>

      {loading ? (
        <div className="flex min-h-[240px] items-center justify-center text-white/70">
          <Loader2 className="mr-2 h-5 w-5 animate-spin" />
          {text.p5GeneratingList}
        </div>
      ) : data ? (
        <div className="space-y-4">
          <div className="flex flex-wrap items-center gap-3">
            <Badge variant="neutral" className="px-4 py-2 text-sm">{text.p5ScannedProducts} {data.total_scanned}</Badge>
            {data.keyword ? <Badge variant="brand" className="px-4 py-2 text-sm">{text.p5KeywordLabel}{data.keyword}</Badge> : null}
            {data.category ? <Badge variant="blue" className="px-4 py-2 text-sm">{text.p5CategoryLabel}{data.category}</Badge> : null}
          </div>
          {data.items.length ? data.items.map((item, index) => (
            <Card key={`p5-rec-${item.product_id}-${index}`}>
              <CardHeader className="flex flex-row items-center justify-between gap-4">
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge variant="brand">TOP {index + 1}</Badge>
                    <StatusBadge
                      status={item.recommendation_score >= 80 ? "success" : item.recommendation_score >= 60 ? "warning" : "blocked"}
                      label={item.recommendation}
                    />
                  </div>
                  <CardTitle className="mt-3">{item.title}</CardTitle>
                  <p className="mt-1 text-sm text-app-text-muted">{item.title_zh || item.keyword}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-app-text-muted">{text.p5RecommendationScore}</p>
                  <p className="text-xl font-semibold text-white">{Math.round(item.recommendation_score)} / 100</p>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4 md:grid-cols-3">
                  <div className="rounded-2xl border border-app-border bg-white/5 p-4">
                    <p className="text-sm text-app-text-muted">{text.p5EstimatedProfit}</p>
                    <p className="mt-2 text-base font-semibold text-white">{item.estimated_profit.toFixed(2)}</p>
                  </div>
                  <div className="rounded-2xl border border-app-border bg-white/5 p-4">
                    <p className="text-sm text-app-text-muted">{text.p5Keyword}</p>
                    <p className="mt-2 text-base font-semibold text-white">{item.keyword}</p>
                  </div>
                  <div className="rounded-2xl border border-app-border bg-white/5 p-4">
                    <p className="text-sm text-app-text-muted">{text.p5Category}</p>
                    <p className="mt-2 text-base font-semibold text-white">{item.category || text.p5Uncategorized}</p>
                  </div>
                </div>
                <div className="rounded-2xl border border-app-border bg-white/5 p-4 shadow-app-soft">
                  <p className="text-sm text-app-text-muted">{text.p5RecommendationReasons}</p>
                  <div className="mt-3 space-y-2">
                    {item.reasons.map((reason) => (
                      <p key={reason} className="text-sm text-app-text-secondary">
                        - {reason}
                      </p>
                    ))}
                  </div>
                </div>
                <Button asChild variant="outline">
                  <Link href={productDetailRoute(item.product_id)}>{text.viewDetail}</Link>
                </Button>
              </CardContent>
            </Card>
          )) : <EmptyState text={text.p5RecommendationEmpty} />}
        </div>
      ) : null}
    </div>
  );
}
