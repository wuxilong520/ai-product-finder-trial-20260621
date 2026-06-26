"use client";

import { useMemo, useState } from "react";
import { Loader2, SearchCheck } from "lucide-react";

import { Badge, Button, Card, EmptyState, InfoTile, Input, LinkTile, MetricTile, ReasonList, StatusAlert } from "@/design-system/components";
import { analyzeFullPublic } from "@/lib/api";
import { useTaskStatus } from "@/hooks/use-task-status";
import { Language, t } from "@/lib/i18n";
import { AnalyzeFullResponse } from "@/lib/types";

const DEFAULT_URL = "https://kyliecosmetics.com/products/matte-lip-kit";

export function AnalyzePanel({ initialLang, initialUrl }: { initialLang: Language; initialUrl?: string }) {
  const [url, setUrl] = useState(initialUrl || DEFAULT_URL);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<AnalyzeFullResponse | null>(null);
  const { state, transport } = useTaskStatus("analyze");

  const text = t(initialLang);
  const okResult = result && "status" in result && result.status === "OK" ? result : null;
  const fallbackResult = result && "status" in result && result.status === "FALLBACK" ? result : null;
  const blockedResult = result && "status" in result && result.status === "BLOCKED" ? result : null;
  const displayResult = okResult || fallbackResult;

  const scoreTone = useMemo(() => {
    const score = displayResult?.score ?? 0;
    if (score >= 70) return "success";
    if (score >= 40) return "warning";
    return "error";
  }, [displayResult]);

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
    <div className="space-y-5">
      <section className="overflow-hidden rounded-[28px] border border-white/8 bg-[#121c2c] p-6 shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
        <div className="grid gap-6 xl:grid-cols-[0.92fr_1.08fr]">
          <div>
            <div className="mt-3 flex flex-wrap gap-3">
              <Badge
                variant={state.status === "success" ? "success" : state.status === "error" ? "error" : state.status === "blocked" ? "blocked" : "running"}
                className="px-4 py-2 text-sm"
              >
                {state.error_reason ? `${state.message}：${state.error_reason}` : state.message}
              </Badge>
            </div>
            <form onSubmit={handleSubmit} className="mt-6 space-y-4">
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
            {fallbackResult ? (
              <StatusAlert status="warning" title={text.aiFallbackTitle} message={text.aiFallbackMessage} />
            ) : null}
          </div>

          <Card variant="panel" className="p-5">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-sm text-app-text-muted">{text.analyzeResultTitle}</p>
                <h3 className="mt-2 text-2xl font-semibold text-white">{displayResult?.title || text.waitingResult}</h3>
              </div>
              <div className={`rounded-2xl border px-4 py-3 text-right ${displayResult ? (scoreTone === "success" ? "border-emerald-400/20 bg-emerald-400/12 text-emerald-300" : scoreTone === "warning" ? "border-amber-400/20 bg-amber-400/12 text-amber-300" : "border-rose-400/20 bg-rose-400/12 text-rose-300") : "border-app-border bg-white/5 text-app-text-muted"}`}>
                <p className="text-xs uppercase tracking-[0.18em]">{text.detailScore}</p>
                <p className="mt-2 text-4xl font-semibold">{displayResult?.score ?? "--"}</p>
              </div>
            </div>

            <div className="mt-4 grid gap-4 md:grid-cols-2">
              <InfoTile label={text.title} value={displayResult?.title || "—"} />
              <InfoTile label={text.detailTitleZh} value={displayResult?.title_zh || "—"} />
              <InfoTile label={text.price} value={displayResult?.price || "—"} />
              <InfoTile label={text.detailCompetition} value={displayResult?.competition_level || "—"} />
            </div>

            <div className="mt-4 grid gap-4 md:grid-cols-2">
              <InfoTile label={text.detailRecommendation} value={displayResult?.recommendation || "—"} />
              <InfoTile label={text.detailProfit} value={displayResult?.profit_estimate || "—"} />
            </div>

            {displayResult?.image ? (
              <div className="mt-4 overflow-hidden rounded-2xl border border-app-border bg-white/5">
                <img src={displayResult.image} alt={displayResult.title} className="h-64 w-full object-cover" />
              </div>
            ) : null}
          </Card>
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-3">
        <CardBlock title={text.analyzeSource}>
          {displayResult ? (
            <div className="space-y-3">
              <LinkTile href={displayResult.source_links["1688_url"]} label={text.open1688} />
              <LinkTile href={displayResult.source_links["pdd_url"]} label={text.openPdd} />
            </div>
          ) : (
            <EmptyState text={text.waitingResult} />
          )}
        </CardBlock>

        <CardBlock title={text.detailKeywords}>
          {displayResult ? <TagList items={displayResult.core_keywords} /> : <EmptyState text={text.waitingResult} />}
        </CardBlock>

        <CardBlock title={text.detailSellingPoints}>
          {displayResult ? <ReasonList items={displayResult.selling_points} /> : <EmptyState text={text.waitingResult} />}
        </CardBlock>
      </section>

      <CardBlock title={text.analyzeReasons}>
        {displayResult ? <ReasonList items={displayResult.reason} /> : <EmptyState text={text.waitingResult} />}
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
