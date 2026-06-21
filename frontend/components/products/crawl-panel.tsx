"use client";

import { useState } from "react";
import Link from "next/link";
import { Link2, Loader2, ScanSearch, Sparkles } from "lucide-react";

import { Badge, Button, Card, CardContent, CardDescription, CardHeader, CardTitle, EmptyState, InfoTile, Input, Label, StatusAlert } from "@/design-system/components";
import { crawlProduct } from "@/lib/api";
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
    <div className="grid gap-6 lg:grid-cols-[1.15fr_0.85fr]">
      <Card className="glow-border">
        <CardHeader>
          <CardTitle>{text.crawlTitleShort}</CardTitle>
          <CardDescription>{text.crawlDescShort}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="mb-5 flex flex-wrap gap-3">
            <Badge variant="brand" className="px-4 py-2 text-sm font-medium">
              <ScanSearch className="h-4 w-4" />
              {text.realExtract}
            </Badge>
            <Badge variant="neutral" className="px-4 py-2 text-sm text-app-text-secondary">
              <Sparkles className="h-4 w-4 text-app-brand-secondary" />
              {text.crawlUnified}
            </Badge>
            <Badge variant={transport === "ws" ? "success" : "warning"} className="px-4 py-2 text-sm">
              {transport === "ws" ? "WS 已连接" : "轮询模式"}
            </Badge>
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
              title="任务状态"
              message={state.error_reason ? `${state.message}：${state.error_reason}` : state.message}
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

      <Card>
        <CardHeader>
          <CardTitle>{text.crawlResultTitle}</CardTitle>
          <CardDescription>{text.crawlResultDesc}</CardDescription>
        </CardHeader>
        <CardContent>
          {result ? (
            <div className="space-y-4">
              <div>
                <p className="text-sm text-app-text-muted">{text.title}</p>
                <p className="mt-1 font-medium text-white">{result.title}</p>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <InfoTile label={text.price} value={result.price || "—"} />
                <InfoTile label={text.rating} value={result.rating || "—"} />
                <InfoTile label={text.reviewCount} value={result.reviews || "—"} />
                <InfoTile label={text.originalUrl} value={result.url} className="break-all" />
              </div>
              <div className="grid grid-cols-2 gap-3">
                {result.images.map((image) => (
                  <img key={image} src={image} alt="product" className="h-32 w-full rounded-2xl border border-app-border object-cover shadow-app-soft" />
                ))}
              </div>
              <div className="flex flex-wrap gap-3">
                {result.product_id ? (
                  <Button asChild variant="outline">
                    <Link href={`/products/${result.product_id}`}>{text.viewProductDetail}</Link>
                  </Button>
                ) : null}
                {result.product_id ? (
                  <Button asChild>
                    <Link href={`/analyze?productId=${result.product_id}`}>{text.continueAi}</Link>
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
