"use client";

import { useMemo, useState } from "react";
import { Loader2, SearchCheck, Sparkles } from "lucide-react";

import { Badge, Button, Card, EmptyState, InfoTile, Input, LinkTile, MetricTile, ReasonList, StatusAlert } from "@/design-system/components";
import { analyzeFullPublic } from "@/lib/api";
import { Language, t } from "@/lib/i18n";
import { AnalyzeFullResponse } from "@/lib/types";

const DEFAULT_URL = "https://kyliecosmetics.com/products/matte-lip-kit";

export function AnalyzePanel({ initialLang }: { initialLang: Language }) {
  const [url, setUrl] = useState(DEFAULT_URL);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<AnalyzeFullResponse | null>(null);

  const text = t(initialLang);
  const okResult = result && "status" in result && result.status === "OK" ? result : null;
  const blockedResult = result && "status" in result && result.status === "BLOCKED" ? result : null;

  const scoreTone = useMemo(() => {
    const score = okResult?.score ?? 0;
    if (score >= 70) return "success";
    if (score >= 40) return "warning";
    return "error";
  }, [okResult]);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
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
    <div className="space-y-6">
      <section className="section-card overflow-hidden">
        <div className="grid gap-8 xl:grid-cols-[1.05fr_0.95fr]">
          <div>
            <Badge variant="brand" className="px-4 py-2 text-sm font-medium">
              <Sparkles className="h-4 w-4" />
              {text.analyzeBadge}
            </Badge>
            <h1 className="gradient-text mt-5 text-4xl font-semibold tracking-tight md:text-5xl">{text.analyzeTitle}</h1>
            <p className="mt-4 max-w-2xl text-lg leading-8 text-app-text-secondary">{text.analyzeDesc}</p>

            <form onSubmit={handleSubmit} className="mt-8 space-y-4">
              <Card className="flex flex-col gap-3 p-3 md:flex-row md:items-center">
                <div className="flex h-12 flex-1 items-center rounded-2xl bg-white/5 px-4">
                  <SearchCheck className="mr-3 h-5 w-5 text-app-brand-secondary" />
                  <Input
                    value={url}
                    onChange={(event) => setUrl(event.target.value)}
                    placeholder={text.analyzePlaceholder}
                    className="w-full border-0 bg-transparent px-0 shadow-none focus:border-0 focus:bg-transparent focus:shadow-none"
                  />
                </div>
                <Button type="submit" disabled={loading}>
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      {text.analyzeLoading}
                    </>
                  ) : (
                    text.analyzeButton
                  )}
                </Button>
              </Card>
            </form>

            {error ? <StatusAlert status="error" message={error} /> : null}

            {blockedResult ? (
              <StatusAlert status="blocked" title={text.analyzeBlockedTitle} message={blockedResult.message || text.analyzeBlockedHint} />
            ) : null}
          </div>

          <Card variant="panel" className="p-6">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-sm text-app-text-muted">{text.analyzeResultTitle}</p>
                <h3 className="mt-2 text-2xl font-semibold text-white">{okResult?.title || text.waitingResult}</h3>
              </div>
              <div className={`rounded-2xl border px-4 py-3 text-right ${okResult ? (scoreTone === "success" ? "border-emerald-400/20 bg-emerald-400/12 text-emerald-300" : scoreTone === "warning" ? "border-amber-400/20 bg-amber-400/12 text-amber-300" : "border-rose-400/20 bg-rose-400/12 text-rose-300") : "border-app-border bg-white/5 text-app-text-muted"}`}>
                <p className="text-xs uppercase tracking-[0.18em]">{text.detailScore}</p>
                <p className="mt-2 text-4xl font-semibold">{okResult?.score ?? "--"}</p>
              </div>
            </div>

            <div className="mt-5 grid gap-4 md:grid-cols-2">
              <InfoTile label={text.title} value={okResult?.title || "—"} />
              <InfoTile label={text.detailTitleZh} value={okResult?.title_zh || "—"} />
              <InfoTile label={text.price} value={okResult?.price || "—"} />
              <InfoTile label={text.detailCompetition} value={okResult?.competition_level || "—"} />
            </div>

            <div className="mt-5 grid gap-4 md:grid-cols-2">
              <InfoTile label={text.detailRecommendation} value={okResult?.recommendation || "—"} />
              <InfoTile label={text.detailProfit} value={okResult?.profit_estimate || "—"} />
            </div>

            {okResult?.image ? (
              <div className="mt-5 overflow-hidden rounded-2xl border border-app-border bg-white/5">
                <img src={okResult.image} alt={okResult.title} className="h-64 w-full object-cover" />
              </div>
            ) : null}
          </Card>
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-3">
        <CardBlock title={text.analyzeSource}>
          {okResult ? (
            <div className="space-y-3">
              <LinkTile href={okResult.source_links["1688_url"]} label={text.open1688} />
              <LinkTile href={okResult.source_links["pdd_url"]} label={text.openPdd} />
            </div>
          ) : (
            <EmptyState text={text.waitingResult} />
          )}
        </CardBlock>

        <CardBlock title={text.detailKeywords}>
          {okResult ? <TagList items={okResult.core_keywords} /> : <EmptyState text={text.waitingResult} />}
        </CardBlock>

        <CardBlock title={text.detailSellingPoints}>
          {okResult ? <ReasonList items={okResult.selling_points} /> : <EmptyState text={text.waitingResult} />}
        </CardBlock>
      </section>

      <CardBlock title={text.analyzeReasons}>
        {okResult ? <ReasonList items={okResult.reason} /> : <EmptyState text={text.waitingResult} />}
      </CardBlock>
    </div>
  );
}

function CardBlock({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <Card className="p-6">
      <p className="text-sm font-medium text-app-text-muted">{title}</p>
      <div className="mt-4">{children}</div>
    </Card>
  );
}

function TagList({ items }: { items: string[] }) {
  return (
    <div className="flex flex-wrap gap-2">
      {items.map((item) => (
        <span key={item} className="rounded-full border border-app-border bg-white/8 px-3 py-2 text-sm font-medium text-app-text-primary">
          {item}
        </span>
      ))}
    </div>
  );
}
