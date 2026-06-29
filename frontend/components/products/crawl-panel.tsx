"use client";

import { useState } from "react";
import Link from "next/link";
import { Link2, Loader2, ScanSearch } from "lucide-react";

import { analyzeWithProductRoute, productDetailRoute } from "@/config/routes";
import { Badge, Button, Card, CardContent, CardDescription, CardHeader, CardTitle, EmptyState, InfoTile, Input, Label, StatusAlert } from "@/design-system/components";
import { crawlProduct } from "@/lib/api-gateway";
import { getToken } from "@/lib/auth";
import { useTaskStatus } from "@/hooks/use-task-status";
import { Language, t } from "@/lib/i18n";
import { CrawlResult } from "@/lib/types";

export function CrawlPanel({ lang }: { lang: Language }) {
  const [url, setUrl] = useState("https://hsp6yx-4x.myshopify.com/products/cute-cat-plush-toy");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<CrawlResult | null>(null);
  const text = t(lang);
  const { state, transport } = useTaskStatus("crawl");

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const data = await crawlProduct(url, getToken());
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : text.crawlFailed);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
      <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
        <CardHeader>
          <CardTitle>采集输入</CardTitle>
          <CardDescription>输入真实商品链接，把它带进这条决策流。</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="mb-5 grid gap-3 md:grid-cols-3">
            <MetricCard label="当前状态" value={state.status} />
            <MetricCard label="同步方式" value={transport === "ws" ? "实时同步" : transport === "polling" ? "自动刷新" : "等待中"} />
            <MetricCard label="流程结果" value={result ? "已进入下一步" : "等待采集"} />
          </div>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="crawl-url">{text.productUrl}</Label>
              <div className="relative">
                <Link2 className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-app-text-muted" />
                <Input id="crawl-url" value={url} onChange={(e) => setUrl(e.target.value)} placeholder={text.analyzePlaceholder} className="pl-9" />
              </div>
            </div>
            <StatusAlert
              status={state.status === "success" ? "success" : state.status === "error" ? "error" : state.status === "blocked" ? "blocked" : "running"}
              title={text.taskStatus}
              message={state.message}
            />
            {error ? <StatusAlert status="error" message={error} /> : null}
            <Button type="submit" disabled={loading} className="w-full sm:w-auto">
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  {text.crawling}
                </>
              ) : (
                text.startCrawl
              )}
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
        <CardHeader>
          <CardTitle>采集结果</CardTitle>
          <CardDescription>这里只保留后续分析和决策真正要用的信息。</CardDescription>
        </CardHeader>
        <CardContent>
          {result ? (
            <div className="space-y-4">
              <div className="grid gap-4 lg:grid-cols-[240px_1fr]">
                <div className="overflow-hidden rounded-[18px] border border-app-border bg-white/5">
                  {result.images[0] ? (
                    <img src={result.images[0]} alt={result.title} className="h-64 w-full object-cover" />
                  ) : (
                    <div className="flex h-64 items-center justify-center text-sm text-white/35">暂无首图</div>
                  )}
                </div>
                <div className="space-y-4">
                  <div>
                    <p className="text-sm text-app-text-muted">{text.title}</p>
                    <p className="mt-1 text-lg font-semibold text-white">{result.title}</p>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <InfoTile label={text.price} value={result.price || "—"} />
                    <InfoTile label={text.rating} value={result.rating || "—"} />
                    <InfoTile label={text.reviewCount} value={result.reviews || "—"} />
                    <InfoTile label={text.originalUrl} value={result.url} className="break-all" />
                  </div>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
                {result.images.slice(0, 4).map((image) => (
                  <img key={image} src={image} alt="product" className="h-28 w-full rounded-2xl border border-app-border object-cover shadow-app-soft" />
                ))}
              </div>
              <div className="flex flex-wrap gap-3">
                <Badge variant="neutral" className="px-4 py-2 text-sm">可继续流转</Badge>
                <Badge variant="brand" className="px-4 py-2 text-sm">{result.product_id ? `商品ID ${result.product_id}` : "未生成商品ID"}</Badge>
              </div>
              <div className="flex flex-wrap gap-3">
                {result.product_id ? (
                  <Button asChild variant="outline">
                    <Link href={productDetailRoute(result.product_id)}>{text.viewProductDetail}</Link>
                  </Button>
                ) : null}
                {result.product_id ? (
                  <Button asChild>
                    <Link href={analyzeWithProductRoute(result.product_id)}>{text.continueAi}</Link>
                  </Button>
                ) : null}
              </div>
            </div>
          ) : (
            <EmptyState text={text.noCrawlResult} />
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-[16px] border border-white/8 bg-white/[0.03] px-4 py-4">
      <div className="text-sm text-white/45">{label}</div>
      <div className="mt-2 text-lg font-semibold text-white">{value}</div>
    </div>
  );
}
