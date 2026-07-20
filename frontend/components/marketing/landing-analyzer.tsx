"use client";

import { useState } from "react";
import { Loader2, SearchCheck } from "lucide-react";

import { Button, Card, CardContent, InfoTile, Input, LinkTile, MetricTile, StatusAlert } from "@/design-system/components";
import { analyzeFullPublic } from "@/lib/api-gateway";
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
    <div className="space-y-5">
      <Card className="rounded-[28px] border border-[#F5E7D4] bg-white p-5 shadow-[0_14px_36px_rgba(15,23,42,0.05)]">
        <div className="rounded-[24px] border border-[#F3E8D8] bg-[linear-gradient(180deg,#FFFFFF,#FFF9F2)] p-6">
          <p className="text-sm font-medium text-[#F97316]">{text.landingDirectFlow}</p>
          <h3 className="mt-3 text-2xl font-semibold tracking-tight text-[#0F172A]">
            {text.landingFlowTitle}
          </h3>
          <p className="mt-3 text-base leading-7 text-[#475569]">
            {text.landingFlowDesc}
          </p>

          <form onSubmit={handleAnalyze} className="mt-6 space-y-4">
            <div className="rounded-[24px] border border-[#F3E8D8] bg-white p-3 shadow-[0_10px_24px_rgba(15,23,42,0.04)]">
              <div className="flex flex-col gap-3 md:flex-row md:items-center">
                <div className="flex h-12 flex-1 items-center rounded-2xl bg-[#FFF7ED] px-4">
                  <SearchCheck className="mr-3 h-5 w-5 text-[#F97316]" />
                <Input
                  value={url}
                  onChange={(event) => setUrl(event.target.value)}
                  className="w-full border-0 bg-transparent px-0 text-[#334155] placeholder:text-[#94A3B8] shadow-none focus:border-0 focus:bg-transparent focus:shadow-none"
                  placeholder={text.analyzePlaceholder}
                />
              </div>
                <Button
                  type="submit"
                  disabled={loading}
                  className="h-12 bg-[linear-gradient(135deg,#FB923C,#F97316)] text-white shadow-[0_14px_30px_rgba(249,115,22,0.22)] hover:-translate-y-0.5 hover:shadow-[0_18px_36px_rgba(249,115,22,0.28)]"
                >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    {text.analyzeLoading}
                  </>
                  ) : (
                    text.startAnalyzing
                  )}
                </Button>
              </div>
            </div>

            {error ? <StatusAlert status="error" message={error} /> : null}
            {blockedResult ? <StatusAlert status="warning" message={blockedResult.message} /> : null}
            {fallbackResult ? <StatusAlert status="warning" title={text.aiFallbackTitle} message={text.aiFallbackMessage} /> : null}
          </form>

          <div className="mt-6 grid gap-3 sm:grid-cols-3">
            <LightMetricTile label={text.landingMetricExtract} value={displayResult ? "OK" : text.statWaiting} />
            <LightMetricTile
              label={text.landingMetricAi}
              value={okResult ? text.statReady : fallbackResult ? text.aiFallbackTitle : loading ? text.statRunning : text.statWaiting}
            />
            <LightMetricTile label={text.landingMetricUi} value={displayResult ? text.statCard : text.statWaiting} />
          </div>
        </div>
      </Card>

      <Card className="rounded-[28px] border border-[#F5E7D4] bg-white p-5 shadow-[0_14px_36px_rgba(15,23,42,0.05)]">
        <div className="rounded-[24px] border border-[#F3E8D8] bg-[linear-gradient(180deg,#FFFFFF,#FFF9F2)] p-6">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-sm text-[#64748B]">{text.analyzeResultTitle}</p>
              <h3 className="mt-2 text-2xl font-semibold tracking-tight text-[#0F172A]">{displayResult?.title || text.productResultCard}</h3>
            </div>
            <div className="rounded-[20px] border border-[#F3E8D8] bg-[#FFF7ED] px-4 py-3 text-right">
              <p className="text-xs uppercase tracking-[0.18em] text-[#94A3B8]">{text.detailScore}</p>
              <p className="mt-2 text-4xl font-semibold text-[#F97316]">{displayResult?.score ?? "--"}</p>
            </div>
          </div>

          <div className="mt-5 grid gap-4 md:grid-cols-2">
            <LightInfoTile label={text.price} value={displayResult?.price || text.waitingResult} />
            <LightInfoTile label={text.detailRecommendation} value={displayResult?.recommendation || text.waitingResult} />
          </div>

          <div className="mt-5">
            <p className="text-sm text-[#64748B]">{text.supplierLinks}</p>
            {displayResult ? (
              <div className="mt-3 grid gap-3">
                <LightLinkTile href={displayResult.source_links["1688_url"]} label="1688" />
                <LightLinkTile href={displayResult.source_links["pdd_url"]} label={text.sourcePdd} />
              </div>
            ) : (
              <p className="mt-3 text-sm text-[#94A3B8]">{text.linksAppearAfterAnalysis}</p>
            )}
          </div>
        </div>
      </Card>
    </div>
  );
}

function LightMetricTile({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-[22px] border border-[#F3E8D8] bg-white px-4 py-4 shadow-[0_8px_22px_rgba(15,23,42,0.04)]">
      <p className="text-[11px] uppercase tracking-[0.18em] text-[#94A3B8]">{label}</p>
      <p className="mt-2 text-lg font-semibold text-[#0F172A]">{value}</p>
    </div>
  );
}

function LightInfoTile({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-[22px] border border-[#F3E8D8] bg-white px-4 py-4 shadow-[0_8px_22px_rgba(15,23,42,0.04)]">
      <p className="text-sm text-[#64748B]">{label}</p>
      <p className="mt-2 text-base font-semibold text-[#0F172A]">{value}</p>
    </div>
  );
}

function LightLinkTile({ href, label }: { href: string; label: string }) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noreferrer"
      className="group flex items-center justify-between rounded-[22px] border border-[#F3E8D8] bg-white px-4 py-3 transition hover:-translate-y-0.5 hover:border-[#FDBA74] hover:bg-[#FFFDF9] hover:shadow-[0_10px_24px_rgba(15,23,42,0.06)]"
    >
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-[#FFF7ED] text-[#F97316]">
          <SearchCheck className="h-4 w-4" />
        </div>
        <span className="font-medium text-[#0F172A]">{label}</span>
      </div>
      <span className="text-sm font-medium text-[#F97316]">查看来源</span>
    </a>
  );
}
