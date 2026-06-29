"use client";

import { useState } from "react";
import { Activity, BarChart3, ExternalLink, Loader2, Search, TrendingUp } from "lucide-react";

import { Badge, Button, Card, CardContent, CardHeader, CardTitle, EmptyState, InfoTile, Input, StatusBadge } from "@/design-system/components";
import { analyzeMarketKeyword, matchSuppliers } from "@/lib/api-gateway";
import { getToken } from "@/lib/auth";
import { Language, t } from "@/lib/i18n";
import type { MarketAnalyzeResponse, SupplierMatchItem } from "@/lib/types";


const DEFAULT_KEYWORD = "air fryer";


export function MarketAnalysisCard({ lang = "zh", initialKeyword }: { lang?: Language; initialKeyword?: string }) {
  const text = t(lang);
  const [keyword, setKeyword] = useState(initialKeyword || DEFAULT_KEYWORD);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<MarketAnalyzeResponse | null>(null);
  const [supplierLoading, setSupplierLoading] = useState(false);
  const [supplierError, setSupplierError] = useState("");
  const [suppliers, setSuppliers] = useState<SupplierMatchItem[]>([]);

  async function handleAnalyze() {
    if (!keyword.trim()) {
      setError(text.marketKeywordRequired);
      return;
    }
    setLoading(true);
    setError("");
    setSupplierError("");
    try {
      const data = await analyzeMarketKeyword(keyword.trim(), getToken());
      setResult(data);
      setSupplierLoading(true);
      try {
        const supplierData = await matchSuppliers(keyword.trim(), getToken());
        setSuppliers(supplierData.suppliers);
      } catch (supplierErr) {
        setSuppliers([]);
        setSupplierError(supplierErr instanceof Error ? supplierErr.message : text.marketSupplierFailed);
      } finally {
        setSupplierLoading(false);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : text.marketAnalyzeFailed);
      setSuppliers([]);
    } finally {
      setLoading(false);
    }
  }

  const currentKeyword = keyword.trim();

  return (
    <Card className="border-white/8 bg-[linear-gradient(180deg,rgba(255,255,255,0.04),rgba(255,255,255,0.02))] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
      <CardHeader className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <div className="flex flex-wrap items-center gap-3">
            <Badge variant="brand" className="px-4 py-2 text-sm font-medium">
              <TrendingUp className="h-4 w-4" />
              {text.marketCardBadge}
            </Badge>
            {result ? <StatusBadge status={toStatus(result.recommendation)} label={toRecommendationLabel(result.recommendation, text)} /> : null}
          </div>
          <CardTitle className="mt-4">{text.marketCardTitle}</CardTitle>
          <p className="mt-2 text-sm text-app-text-muted">{text.marketCardDesc}</p>
        </div>
        <div className="flex w-full max-w-xl gap-2">
          <div className="relative flex-1">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-app-text-muted" />
            <Input value={keyword} onChange={(event) => setKeyword(event.target.value)} placeholder={text.marketKeywordPlaceholder} className="pl-9" />
          </div>
          <Button type="button" onClick={handleAnalyze} disabled={loading}>
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                {text.marketAnalyzing}
              </>
            ) : (
              text.marketAnalyzeButton
            )}
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-5">
        {error ? <div className="rounded-2xl border border-rose-400/20 bg-rose-400/10 px-4 py-3 text-sm text-rose-200">{error}</div> : null}
        {result ? (
          <>
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              <MetricInfoTile label={text.marketTrendScore} value={`${Math.round(result.trend_score)} / 100`} icon={<TrendingUp className="h-4 w-4" />} />
              <MetricInfoTile label={text.marketDemandScore} value={`${Math.round(result.demand_score)} / 100`} icon={<Activity className="h-4 w-4" />} />
              <MetricInfoTile label={text.marketCompetitionScore} value={`${Math.round(result.competition_score)} / 100`} icon={<BarChart3 className="h-4 w-4" />} />
              <MetricInfoTile label={text.marketOpportunityScore} value={`${Math.round(result.opportunity_score)} / 100`} icon={<TrendingUp className="h-4 w-4" />} />
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <InfoTile label={text.marketRecommendationScore} value={`${Math.round(result.recommendation_score)} / 100`} />
              <InfoTile label={text.marketCategory} value={result.category || text.marketUnknownCategory} />
            </div>
            {currentKeyword ? (
              <div className="grid gap-4 md:grid-cols-2">
                <InfoTile label={text.marketKeywordLabel} value={currentKeyword} />
                <InfoTile label={text.marketSourceLabel} value={result.source} />
              </div>
            ) : null}
            <div className="rounded-2xl border border-app-border bg-white/5 p-4 shadow-app-soft">
              <p className="text-sm text-app-text-muted">{text.marketReasons}</p>
              <div className="mt-3 space-y-2">
                {result.reasons.map((item) => (
                  <p key={item} className="text-sm text-app-text-secondary">
                    - {item}
                  </p>
                ))}
              </div>
            </div>
            <div className="rounded-2xl border border-app-border bg-white/5 p-4 shadow-app-soft">
              <div className="flex items-center justify-between gap-3">
                <p className="text-sm text-app-text-muted">{text.marketSupplierTitle}</p>
                {supplierLoading ? <Badge variant="neutral">{text.marketSupplierLoading}</Badge> : null}
              </div>
              {supplierError ? <div className="mt-3 text-sm text-rose-200">{supplierError}</div> : null}
              {suppliers.length ? (
                <div className="mt-4 space-y-3">
                  {suppliers.map((supplier, index) => (
                    <a
                      key={`${supplier.platform}-${supplier.supplier_url}-${index}`}
                      href={supplier.supplier_url}
                      target="_blank"
                      rel="noreferrer"
                      className="flex flex-col gap-3 rounded-2xl border border-app-border bg-white/4 p-4 transition hover:border-app-border-strong hover:bg-white/8"
                    >
                      <div className="flex flex-wrap items-center justify-between gap-3">
                        <div className="flex flex-wrap items-center gap-2">
                          <Badge variant="brand">{supplier.platform}</Badge>
                          <StatusBadge status={supplier.match_score >= 70 ? "success" : supplier.match_score >= 45 ? "warning" : "blocked"} label={`${text.marketMatchScore} ${Math.round(supplier.match_score)}`} />
                        </div>
                        <div className="flex items-center gap-2 text-sm text-app-brand-secondary">
                          <ExternalLink className="h-4 w-4" />
                          {text.marketSupplierOpen}
                        </div>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-white">{supplier.supplier_title}</p>
                        <p className="mt-1 text-xs text-app-text-muted">{supplier.supplier_name || supplier.availability}</p>
                      </div>
                      <div className="grid gap-3 md:grid-cols-3">
                        <InfoTile label={text.marketSupplierPlatform} value={supplier.platform} />
                        <InfoTile label={text.marketSupplierPrice} value={formatSupplierPrice(supplier, text.marketSupplierPendingPrice)} />
                        <InfoTile label={text.marketSupplierStatus} value={supplier.availability} />
                      </div>
                    </a>
                  ))}
                </div>
              ) : supplierLoading ? null : (
                <div className="mt-3">
                  <EmptyState text={text.marketSupplierEmpty} />
                </div>
              )}
            </div>
          </>
        ) : (
          <EmptyState text={text.marketNoResult} />
        )}
      </CardContent>
    </Card>
  );
}

function toStatus(value: string) {
  if (value === "推荐关注") return "success";
  if (value === "继续观察") return "warning";
  if (value === "Recommend" || value === "Recommended") return "success";
  if (value === "Monitor") return "warning";
  return "blocked";
}

function toRecommendationLabel(value: string, text: ReturnType<typeof t>) {
  if (value === "推荐关注" || value === "Recommend" || value === "Recommended") {
    return text.productIntelRecommendReady;
  }
  if (value === "继续观察" || value === "Monitor") {
    return text.productIntelRecommendWatch;
  }
  return text.productIntelRecommendSkip;
}

function MetricInfoTile({ label, value, icon }: { label: string; value: string; icon: React.ReactNode }) {
  return (
    <div className="rounded-2xl border border-app-border bg-white/5 p-4 shadow-app-soft">
      <div className="flex items-center gap-2 text-app-text-muted">
        <span className="text-app-brand-secondary">{icon}</span>
        <p className="text-sm">{label}</p>
      </div>
      <p className="mt-2 text-base font-semibold text-white">{value}</p>
    </div>
  );
}

function formatSupplierPrice(supplier: SupplierMatchItem, fallback: string) {
  if (supplier.supplier_price == null) {
    return fallback;
  }
  const amount = Number(supplier.supplier_price).toFixed(2);
  return supplier.currency ? `${supplier.currency} ${amount}` : amount;
}
