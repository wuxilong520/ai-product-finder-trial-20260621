"use client";

import { useEffect, useMemo, useState } from "react";
import { Activity, AlertTriangle, BarChart3, ExternalLink, Loader2, Search, ShoppingBag, TrendingUp } from "lucide-react";

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

  useEffect(() => {
    if (initialKeyword && initialKeyword !== keyword) {
      setKeyword(initialKeyword);
    }
  }, [initialKeyword, keyword]);

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
  const competitionLevel = result?.competition_level || scoreToLevel(result?.competition_score ?? null);
  const marketSaturation = result?.market_saturation ?? result?.competition_score ?? null;
  const confidencePercent = result?.confidence != null ? Math.round(result.confidence * 100) : null;
  const marketScore = result?.market_score ?? result?.opportunity_score ?? null;
  const platformSignals = result?.platform_signals;
  const relatedKeywords = result?.keyword_cluster?.related_keywords || [];
  const longTailKeywords = result?.keyword_cluster?.long_tail_keywords || [];
  const platformCompatibility = result?.platform_compatibility;
  const riskHints = useMemo(() => {
    if (!result) return [];
    const apiFlags = result.risk_flags || [];
    const uiFlags = [
      result.is_mock ? "mock_data_used" : null,
      confidencePercent != null && confidencePercent < 60 ? "low_confidence" : null,
    ].filter(Boolean) as string[];
    return Array.from(new Set([...apiFlags, ...uiFlags]));
  }, [result, confidencePercent]);

  return (
    <Card className="border-white/8 bg-[linear-gradient(180deg,rgba(255,255,255,0.04),rgba(255,255,255,0.02))] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
      <CardHeader className="space-y-4">
        <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
          <div className="max-w-3xl">
            <div className="flex flex-wrap items-center gap-3">
              <Badge variant="brand" className="px-4 py-2 text-sm font-medium">
                <TrendingUp className="h-4 w-4" />
                市场智能层
              </Badge>
              {result ? (
                <StatusBadge status={toStatus(result.recommendation)} label={toRecommendationLabel(result.recommendation)} />
              ) : null}
            </div>
            <CardTitle className="mt-4">先判断这个方向值不值得做</CardTitle>
            <p className="mt-2 text-sm leading-7 text-app-text-muted">
              先看需求、趋势、竞争和进入难度，再决定要不要继续进入商品机会页和 1688 匹配页。
            </p>
          </div>
          <div className="flex w-full max-w-xl gap-2">
            <div className="relative flex-1">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-app-text-muted" />
              <Input value={keyword} onChange={(event) => setKeyword(event.target.value)} placeholder="例如：炒锅、空气炸锅、电热饭盒" className="pl-9" />
            </div>
            <Button type="button" onClick={handleAnalyze} disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  分析中
                </>
              ) : (
                "开始分析"
              )}
            </Button>
          </div>
        </div>
        <div className="grid gap-4 md:grid-cols-4">
          <InfoTile label="这页回答什么" value="这个方向能不能做" />
          <InfoTile label="先看什么" value="需求、趋势、竞争" />
          <InfoTile label="再做什么" value="筛商品和供应链" />
          <InfoTile label="最后目标" value="找到能卖的 SKU" />
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {error ? <div className="rounded-2xl border border-rose-400/20 bg-rose-400/10 px-4 py-3 text-sm text-rose-200">{error}</div> : null}

        {!result ? (
          <EmptyState text="先输入一个关键词，例如炒锅或空气炸锅。系统会先告诉你这个方向值不值得继续做。" />
        ) : (
          <>
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
              <MetricInfoTile label="需求评分" value={formatScore(result.demand_score)} icon={<Activity className="h-4 w-4" />} />
              <MetricInfoTile label="趋势强度" value={formatScore(result.trend_score)} icon={<TrendingUp className="h-4 w-4" />} />
              <MetricInfoTile label="竞争强度" value={levelText(competitionLevel)} icon={<BarChart3 className="h-4 w-4" />} />
              <MetricInfoTile label="市场饱和度" value={formatScore(marketSaturation)} icon={<BarChart3 className="h-4 w-4" />} />
              <MetricInfoTile label="市场结论" value={result.recommendation} icon={<ShoppingBag className="h-4 w-4" />} />
            </div>

            <div className="grid gap-4 xl:grid-cols-3">
              <Card className="border-white/8 bg-white/5">
                <CardHeader>
                  <CardTitle className="text-lg">市场进入判断</CardTitle>
                </CardHeader>
                <CardContent className="grid gap-3">
                  <InfoTile label="市场机会分" value={formatScore(marketScore)} />
                  <InfoTile label="推荐分" value={formatScore(result.recommendation_score)} />
                  <InfoTile label="进入难度" value={levelText(result.entry_barrier)} />
                  <InfoTile label="当前类目" value={result.category || text.marketUnknownCategory} />
                  <InfoTile label="可信度" value={confidencePercent != null ? `${confidencePercent} / 100` : "当前没有返回"} />
                </CardContent>
              </Card>

              <Card className="border-white/8 bg-white/5 xl:col-span-2">
                <CardHeader>
                  <CardTitle className="text-lg">为什么给这个结论</CardTitle>
                </CardHeader>
                <CardContent className="grid gap-3 md:grid-cols-3">
                  <ReasonBox title="需求判断" value={result.reasoning?.demand_reason || firstReason(result.reasons, 1)} />
                  <ReasonBox title="竞争判断" value={result.reasoning?.competition_reason || firstReason(result.reasons, 3)} />
                  <ReasonBox title="趋势判断" value={result.reasoning?.trend_reason || firstReason(result.reasons, 2)} />
                </CardContent>
              </Card>
            </div>

            <div className="grid gap-4 xl:grid-cols-4">
              <SignalCard label="Google 趋势" value={formatScore(platformSignals?.google_trends_score ?? null)} />
              <SignalCard label="Amazon 搜索" value={formatScore(platformSignals?.amazon_search_volume ?? null)} />
              <SignalCard label="TikTok 热度" value={formatScore(platformSignals?.tiktok_viral_score ?? null)} />
              <SignalCard label="Shopify 活跃度" value={formatScore(platformSignals?.shopify_category_activity ?? null)} />
            </div>

            <div className="grid gap-4 xl:grid-cols-2">
              <Card className="border-white/8 bg-white/5">
                <CardHeader>
                  <CardTitle className="text-lg">关键词延展</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <KeywordGroup title="相关词" items={relatedKeywords} emptyText="当前还没有返回相关词。" />
                  <KeywordGroup title="长尾词" items={longTailKeywords} emptyText="当前还没有返回长尾词。" />
                </CardContent>
              </Card>

              <Card className="border-white/8 bg-white/5">
                <CardHeader>
                  <CardTitle className="text-lg">平台落地性判断</CardTitle>
                </CardHeader>
                <CardContent className="grid gap-3">
                  <InfoTile label="Shopify 适配" value={boolText(platformCompatibility?.shopify_ready)} />
                  <InfoTile label="TikTok 潜力" value={formatScore(platformCompatibility?.tiktok_potential ?? null)} />
                  <InfoTile
                    label="1688 匹配词"
                    value={platformCompatibility?.alibaba_match?.length ? platformCompatibility.alibaba_match.join(" / ") : "当前还没有匹配词"}
                  />
                </CardContent>
              </Card>
            </div>

            <div className="grid gap-4 xl:grid-cols-2">
              <Card className="border-white/8 bg-white/5">
                <CardHeader>
                  <CardTitle className="text-lg">风险提示</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {riskHints.length ? riskHints.map((item) => (
                    <div key={item} className="flex items-start gap-3 rounded-2xl border border-white/8 bg-black/10 px-4 py-3">
                      <AlertTriangle className="mt-0.5 h-4 w-4 text-[#FFB020]" />
                      <div className="text-sm leading-7 text-white/70">{riskFlagText(item)}</div>
                    </div>
                  )) : (
                    <EmptyState text="当前没有明显风险提示。" />
                  )}
                </CardContent>
              </Card>

              <Card className="border-white/8 bg-white/5">
                <CardHeader>
                  <CardTitle className="text-lg">这页当前说真话</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3 text-sm leading-7 text-white/68">
                  <p>当前市场页已经能真实展示：需求、趋势、竞争、市场分、风险标记、平台兼容性和关键词扩展。</p>
                  <p>但它现在还不是“真实外部平台全量数据”，因为 Google / Amazon / TikTok / Shopify 市场源里仍然有 mock 或 partial 情况。</p>
                  <p>所以这页现在能用来做第一层商业判断，但还不能假装等同于完全真实全网市场数据。</p>
                </CardContent>
              </Card>
            </div>

            <div className="rounded-2xl border border-app-border bg-white/5 p-4 shadow-app-soft">
              <div className="flex items-center justify-between gap-3">
                <p className="text-sm text-app-text-muted">1688 / 供应链匹配结果</p>
                {supplierLoading ? <Badge variant="neutral">正在匹配</Badge> : null}
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
                          <StatusBadge
                            status={supplier.match_score >= 70 ? "success" : supplier.match_score >= 45 ? "warning" : "blocked"}
                            label={`匹配分 ${Math.round(supplier.match_score)}`}
                          />
                        </div>
                        <div className="flex items-center gap-2 text-sm text-app-brand-secondary">
                          <ExternalLink className="h-4 w-4" />
                          打开供应链接
                        </div>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-white">{supplier.supplier_title}</p>
                        <p className="mt-1 text-xs text-app-text-muted">{supplier.supplier_name || supplier.availability}</p>
                      </div>
                      <div className="grid gap-3 md:grid-cols-3">
                        <InfoTile label="平台" value={supplier.platform} />
                        <InfoTile label="价格" value={formatSupplierPrice(supplier, "等待价格")} />
                        <InfoTile label="状态" value={supplier.availability} />
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

            <div className="rounded-2xl border border-app-border bg-white/5 p-4 shadow-app-soft">
              <p className="text-sm text-app-text-muted">当前分析关键词与数据来源</p>
              <div className="mt-4 grid gap-4 md:grid-cols-2">
                <InfoTile label="分析关键词" value={currentKeyword} />
                <InfoTile label="分析来源" value={result.source} />
              </div>
              {result.data_source_map ? (
                <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
                  {Object.entries(result.data_source_map).map(([key, value]) => (
                    <InfoTile key={key} label={key} value={value} />
                  ))}
                </div>
              ) : null}
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}

function toStatus(value: string) {
  if (value === "BUY" || value === "推荐关注" || value === "Recommend" || value === "Recommended") return "success";
  if (value === "TEST" || value === "继续观察" || value === "Monitor") return "warning";
  return "blocked";
}

function toRecommendationLabel(value: string) {
  if (value === "BUY" || value === "推荐关注") return "值得继续做";
  if (value === "TEST" || value === "继续观察") return "先观察";
  return "暂时放弃";
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

function SignalCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/8 bg-white/[0.03] p-4">
      <div className="text-sm text-white/48">{label}</div>
      <div className="mt-2 text-xl font-semibold text-white">{value}</div>
    </div>
  );
}

function ReasonBox({ title, value }: { title: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/8 bg-black/10 p-4">
      <div className="text-sm font-medium text-white">{title}</div>
      <div className="mt-2 text-sm leading-7 text-white/65">{value}</div>
    </div>
  );
}

function KeywordGroup({ title, items, emptyText }: { title: string; items: string[]; emptyText: string }) {
  return (
    <div>
      <div className="text-sm font-medium text-white">{title}</div>
      <div className="mt-3 flex flex-wrap gap-2">
        {items.length ? items.map((item) => (
          <span key={item} className="rounded-full border border-white/8 bg-white/[0.03] px-3 py-1.5 text-sm text-white/70">
            {item}
          </span>
        )) : (
          <span className="text-sm text-white/45">{emptyText}</span>
        )}
      </div>
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

function formatScore(value: number | null | undefined) {
  if (value == null || Number.isNaN(value)) {
    return "当前没有返回";
  }
  return `${Math.round(value)} / 100`;
}

function scoreToLevel(value: number | null) {
  if (value == null) return "unknown";
  if (value >= 70) return "high";
  if (value >= 45) return "medium";
  return "low";
}

function levelText(value?: string | null) {
  if (value === "high") return "高";
  if (value === "medium") return "中";
  if (value === "low") return "低";
  if (value === "unknown" || !value) return "当前没有返回";
  return value;
}

function boolText(value?: boolean | null) {
  if (value === true) return "可以继续准备";
  if (value === false) return "暂时不建议直接推进";
  return "当前没有返回";
}

function firstReason(reasons: string[], index: number) {
  return reasons[index] || reasons[0] || "当前没有更多说明。";
}

function riskFlagText(flag: string) {
  if (flag === "low_demand") return "需求偏弱：这个方向当前需求基础不够强。";
  if (flag === "high_competition") return "竞争偏高：这个方向当前竞争压力比较大。";
  if (flag === "unstable_trend") return "趋势不稳：最近增长趋势不够稳定。";
  if (flag === "mock_data_used") return "使用了 mock 数据：这次判断里有模拟数据参与。";
  if (flag === "low_confidence") return "可信度偏低：当前信号样本还不够强。";
  return flag;
}
