"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { Loader2, Sparkles, Wand2 } from "lucide-react";

import { Button, Card, EmptyState, InfoTile, Input, ReasonList, StatusAlert } from "@/design-system/components";
import { analyzeFullPublic } from "@/lib/api-gateway";
import { Language, t } from "@/lib/i18n";
import { AnalyzeFullResponse } from "@/lib/types";

const SAMPLE_URL = "https://kyliecosmetics.com/products/matte-lip-kit";

export function ProductDemoPanel({ initialLang }: { initialLang: Language }) {
  const [url, setUrl] = useState(SAMPLE_URL);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<AnalyzeFullResponse | null>(null);

  const text = t(initialLang);

  const okResult = result && "status" in result && result.status === "OK" ? result : null;
  const fallbackResult = result && "status" in result && result.status === "FALLBACK" ? result : null;
  const blockedResult = result && "status" in result && result.status === "BLOCKED" ? result : null;
  const displayResult = okResult || fallbackResult;

  const scoreTone = useMemo(() => {
    const score = displayResult?.product_score ?? 0;
    if (score >= 70) return "text-emerald-300 border-emerald-400/20 bg-emerald-400/12";
    if (score >= 40) return "text-amber-300 border-amber-400/20 bg-amber-400/12";
    return "text-rose-300 border-rose-400/20 bg-rose-400/12";
  }, [displayResult]);

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

  return (
    <section className="grid gap-8 lg:grid-cols-[1.02fr_0.98fr]">
      <Card variant="panel" className="glow-border p-6">
        <div className="rounded-[28px] border border-app-border bg-white/5 p-6 md:p-8">
          <p className="text-sm text-app-brand-secondary">{text.trialDemoBadge}</p>
          <h1 className="gradient-text mt-3 text-4xl font-semibold tracking-tight md:text-5xl">{text.trialDemoTitle}</h1>
          <p className="mt-4 max-w-2xl text-lg leading-8 text-app-text-secondary">{text.trialDemoDesc}</p>

          <form onSubmit={handleAnalyze} className="mt-8 space-y-4">
            <Card className="flex flex-col gap-3 p-3 md:flex-row md:items-center">
              <div className="flex h-12 flex-1 items-center rounded-2xl bg-white/5 px-4">
                <Wand2 className="mr-3 h-5 w-5 text-app-brand-secondary" />
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
                  text.trialDemoButton
                )}
              </Button>
            </Card>

            <div className="flex flex-wrap gap-3">
              <Button
                type="button"
                variant="secondary"
                onClick={() => setUrl(SAMPLE_URL)}
              >
                <Sparkles className="mr-2 h-4 w-4" />
                {text.trialDemoUseExample}
              </Button>
              <Link
                href={SAMPLE_URL}
                target="_blank"
                className="inline-flex items-center rounded-2xl border border-app-border bg-white/5 px-4 py-3 text-sm text-app-text-secondary transition hover:border-app-border-strong hover:bg-white/8"
              >
                {text.trialDemoExample}
              </Link>
            </div>
          </form>

          <div className="mt-5 space-y-3">
            {error ? <StatusAlert status="error" message={error} /> : null}
            {blockedResult ? <StatusAlert status="blocked" title={text.analyzeBlockedTitle} message={blockedResult.message} /> : null}
            {fallbackResult ? <StatusAlert status="warning" title={text.aiFallbackTitle} message={text.aiFallbackMessage} /> : null}
          </div>
        </div>
      </Card>

      <Card variant="panel" className="p-6">
        <div className="rounded-[28px] border border-app-border bg-white/5 p-6 md:p-8">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-sm text-app-text-muted">{text.analyzeResultTitle}</p>
              <h2 className="mt-2 text-2xl font-semibold text-white">{displayResult?.title || text.waitingResult}</h2>
            </div>
            <div className={`rounded-2xl border px-4 py-3 text-right ${displayResult ? scoreTone : "border-app-border bg-white/5 text-app-text-muted"}`}>
              <p className="text-xs uppercase tracking-[0.18em]">{text.detailScore}</p>
              <p className="mt-2 text-4xl font-semibold">{displayResult?.product_score ?? "--"}</p>
            </div>
          </div>

          <div className="mt-5 grid gap-4 md:grid-cols-2">
            <InfoTile label={text.detailRecommendation} value={displayResult?.recommendation || "—"} />
            <InfoTile label={text.price} value={displayResult?.price || "—"} />
          </div>

          <div className="mt-5">
            <p className="text-sm text-app-text-muted">{text.trialDemoReason}</p>
            <div className="mt-3">
              {displayResult ? (
                <ReasonList items={displayResult.reason} />
              ) : (
                <EmptyState text={text.waitingResult} />
              )}
            </div>
          </div>
        </div>
      </Card>
    </section>
  );
}
