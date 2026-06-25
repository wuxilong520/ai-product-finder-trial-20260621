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

  const okResult = result && "status" in result && result.status === "OK" ? result : null;
  const fallbackResult = result && "status" in result && result.status === "FALLBACK" ? result : null;
  const blockedResult = result && "status" in result && result.status === "BLOCKED" ? result : null;
  const displayResult = okResult || fallbackResult;

  return (
    <div className="mt-12 grid gap-8 lg:grid-cols-[1.08fr_0.92fr]">
      <Card variant="panel" className="glow-border p-5">
        <div className="rounded-[24px] border border-app-border bg-white/5 p-6">
          <p className="text-sm text-app-brand-secondary">{text.landingDirectFlow}</p>
          <h3 className="mt-3 text-3xl font-semibold tracking-tight text-white">
            {text.landingFlowTitle}
          </h3>
          <p className="mt-3 text-base leading-7 text-app-text-secondary">
            {text.landingFlowDesc}
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
            {fallbackResult ? <StatusAlert status="warning" title={text.aiFallbackTitle} message={text.aiFallbackMessage} /> : null}
          </form>

          <div className="mt-6 grid gap-3 sm:grid-cols-3">
            <MetricTile label={text.landingMetricExtract} value={displayResult ? "OK" : text.statWaiting} />
            <MetricTile label={text.landingMetricAi} value={okResult ? text.statReady : fallbackResult ? text.aiFallbackTitle : loading ? text.statRunning : text.statWaiting} />
            <MetricTile label={text.landingMetricUi} value={displayResult ? text.statCard : text.statWaiting} />
          </div>
        </div>
      </Card>

      <Card variant="panel" className="p-5">
        <div className="rounded-[24px] border border-app-border bg-white/5 p-6">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-sm text-app-text-muted">{text.analyzeResultTitle}</p>
              <h3 className="mt-2 text-2xl font-semibold tracking-tight text-white">{displayResult?.title || text.productResultCard}</h3>
            </div>
            <div className="rounded-[20px] border border-app-border bg-white/6 px-4 py-3 text-right">
              <p className="text-xs uppercase tracking-[0.18em] text-app-text-muted">{text.detailScore}</p>
              <p className="mt-2 text-4xl font-semibold text-white">{displayResult?.score ?? "--"}</p>
            </div>
          </div>

          <div className="mt-5 grid gap-4 md:grid-cols-2">
            <InfoTile label={text.price} value={displayResult?.price || text.waitingResult} />
            <InfoTile label={text.detailRecommendation} value={displayResult?.recommendation || text.waitingResult} />
          </div>

          <div className="mt-5">
            <p className="text-sm text-app-text-muted">{text.supplierLinks}</p>
            {displayResult ? (
              <div className="mt-3 grid gap-3">
                <LinkTile href={displayResult.source_links["1688_url"]} label="1688" />
                <LinkTile href={displayResult.source_links["pdd_url"]} label={text.sourcePdd} />
              </div>
            ) : (
              <p className="mt-3 text-sm text-app-text-muted">{text.linksAppearAfterAnalysis}</p>
            )}
          </div>
        </div>
      </Card>
    </div>
  );
}
