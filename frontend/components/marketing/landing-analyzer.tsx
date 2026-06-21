"use client";

import { useState } from "react";
import { Loader2, SearchCheck } from "lucide-react";

import { Button, Card, CardContent, InfoTile, Input, LinkTile, MetricTile, StatusAlert } from "@/design-system/components";
import { analyzeFullPublic } from "@/lib/api";
import { Language, t } from "@/lib/i18n";
import { AnalyzeFullResponse } from "@/lib/types";

const defaultUrl = "https://kyliecosmetics.com/products/matte-lip-kit";

export function LandingAnalyzer({ initialLang }: { initialLang: Language }) {
  const [url, setUrl] = useState(defaultUrl);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<AnalyzeFullResponse | null>(null);
  const text = t(initialLang);

  async function handleAnalyze(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const data = await analyzeFullPublic(url, initialLang);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : text.analyzeFriendlyError);
    } finally {
      setLoading(false);
    }
  }

  const okResult = result?.status === "OK" ? result : null;
  const blockedResult = result?.status === "BLOCKED" ? result : null;

  return (
    <div className="mt-12 grid gap-8 lg:grid-cols-[1.08fr_0.92fr]">
      <Card variant="panel" className="glow-border p-5">
        <div className="rounded-[24px] border border-app-border bg-white/5 p-6">
          <p className="text-sm text-app-brand-secondary">{initialLang === "zh" ? "直接体验完整流程" : "Try full flow now"}</p>
          <h3 className="mt-3 text-3xl font-semibold tracking-tight text-white">
            {initialLang === "zh" ? "输入链接 → 自动分析 → 直接看结论" : "Paste URL → Analyze → See the answer"}
          </h3>
          <p className="mt-3 text-base leading-7 text-app-text-secondary">
            {initialLang === "zh"
              ? "首页直接能用，不需要先研究接口。"
              : "Use it from the homepage directly without learning the API first."}
          </p>

          <form onSubmit={handleAnalyze} className="mt-6 space-y-4">
            <Card className="flex flex-col gap-3 p-3 md:flex-row md:items-center">
              <div className="flex h-12 flex-1 items-center rounded-2xl bg-white/5 px-4">
                <SearchCheck className="mr-3 h-5 w-5 text-app-brand-secondary" />
                <Input
                  value={url}
                  onChange={(event) => setUrl(event.target.value)}
                  className="w-full border-0 bg-transparent px-0 shadow-none focus:border-0 focus:bg-transparent focus:shadow-none"
                  placeholder={text.analyzePlaceholder}
                />
              </div>
              <Button type="submit" disabled={loading}>
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    {text.analyzeLoading}
                  </>
                  ) : (
                    text.startAnalyzing
                  )}
              </Button>
            </Card>

            {error ? <StatusAlert status="error" message={error} /> : null}
            {blockedResult ? <StatusAlert status="warning" message={blockedResult.message} /> : null}
          </form>

          <div className="mt-6 grid gap-3 sm:grid-cols-3">
            <MetricTile label="Extract" value={okResult ? "OK" : text.statWaiting} />
            <MetricTile label="AI" value={okResult ? text.statReady : loading ? text.statRunning : text.statWaiting} />
            <MetricTile label="UI" value={okResult ? text.statCard : text.statWaiting} />
          </div>
        </div>
      </Card>

      <Card variant="panel" className="p-5">
        <div className="rounded-[24px] border border-app-border bg-white/5 p-6">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-sm text-app-text-muted">{text.analyzeResultTitle}</p>
              <h3 className="mt-2 text-2xl font-semibold tracking-tight text-white">{okResult?.title || "Product result card"}</h3>
            </div>
            <div className="rounded-[20px] border border-app-border bg-white/6 px-4 py-3 text-right">
              <p className="text-xs uppercase tracking-[0.18em] text-app-text-muted">{text.detailScore}</p>
              <p className="mt-2 text-4xl font-semibold text-white">{okResult?.score ?? "--"}</p>
            </div>
          </div>

          <div className="mt-5 grid gap-4 md:grid-cols-2">
            <InfoTile label={text.price} value={okResult?.price || text.waitingResult} />
            <InfoTile label={text.detailRecommendation} value={okResult?.recommendation || text.waitingResult} />
          </div>

          <div className="mt-5">
            <p className="text-sm text-app-text-muted">{text.supplierLinks}</p>
            {okResult ? (
              <div className="mt-3 grid gap-3">
                <LinkTile href={okResult.source_links["1688_url"]} label="1688" />
                <LinkTile href={okResult.source_links["pdd_url"]} label="Pinduoduo" />
              </div>
            ) : (
              <p className="mt-3 text-sm text-app-text-muted">{initialLang === "zh" ? "分析完成后这里会变成可点链接。" : "Links appear after analysis."}</p>
            )}
          </div>
        </div>
      </Card>
    </div>
  );
}
