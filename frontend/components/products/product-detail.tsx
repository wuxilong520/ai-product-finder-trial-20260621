import Link from "next/link";

import { Badge, Button, Card, CardContent, CardHeader, CardTitle, EmptyState, InfoTile } from "@/design-system/components";
import { AnalyzeResponse, Product } from "@/lib/types";
import { Language } from "@/lib/i18n";

export function ProductDetail({
  product,
  analysisReport,
  lang,
}: {
  product: Product;
  analysisReport?: AnalyzeResponse | null;
  lang: Language;
}) {
  const productImages = Array.isArray(product.images) ? product.images : [];
  const safeSourceUrl = toSafeHttpUrl(product.source_url);
  const analysis = analysisReport?.analysis;
  const intelligence = analysisReport?.intelligence;

  return (
    <div className="space-y-6">
      <Card className="border-white/8 bg-[linear-gradient(135deg,rgba(79,124,255,0.12),rgba(17,26,46,0.96))]">
        <CardContent className="grid gap-6 p-6 xl:grid-cols-[1.1fr_0.9fr]">
          <div className="space-y-5">
            <div className="flex flex-wrap items-center gap-2">
              <Badge variant="brand">AI商业分析报告</Badge>
              <Badge variant="neutral">{product.is_active ? "已进入机会库" : "待激活"}</Badge>
            </div>
            <div>
              <h2 className="text-2xl font-semibold text-white">{product.title_zh || product.title}</h2>
              <p className="mt-2 text-sm leading-7 text-white/60">{product.title}</p>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <InfoTile label="市场机会指数" value={intelligence ? `${intelligence.product_score}/100` : "待生成"} />
              <InfoTile label="利润空间预测" value={intelligence?.profit_estimate || "待生成"} />
              <InfoTile label="竞争热度" value={toCompetitionLabel(intelligence?.competition_level)} />
              <InfoTile label="AI进入建议" value={toRecommendationLabel(intelligence?.recommendation)} />
            </div>
            <div className="rounded-2xl border border-white/8 bg-black/10 p-4 text-sm leading-7 text-white/68">
              {intelligence?.reason?.length
                ? intelligence.reason.slice(0, 3).join("；")
                : "这里会把这个商品为什么值得看、哪里需要小心、下一步该去哪一页继续判断，用大白话告诉你。"}
            </div>
            <div className="flex flex-wrap gap-3">
              <Button asChild>
                <Link href={`/insights?keyword=${encodeURIComponent(product.title_zh || product.title)}`}>继续看市场分析</Link>
              </Button>
              <Button asChild variant="secondary">
                <Link href={`/action-center/procurement?keyword=${encodeURIComponent(product.title_zh || product.title)}`}>放入智能采购方案</Link>
              </Button>
              <Button asChild variant="outline">
                <Link href={`/action-center/suppliers?keyword=${encodeURIComponent(product.title_zh || product.title)}`}>查看供应方案</Link>
              </Button>
            </div>
          </div>

          <div className="space-y-4">
            {productImages[0]?.image_url ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={productImages[0].image_url} alt={product.title} className="h-[320px] w-full rounded-[28px] border border-white/8 object-cover" />
            ) : (
              <div className="flex h-[320px] items-center justify-center rounded-[28px] border border-white/8 bg-white/5 text-sm text-white/45">
                暂无商品图片
              </div>
            )}
            <div className="grid gap-3 md:grid-cols-2">
              <InfoTile label="当前价格" value={product.current_price == null ? "待补充" : `${product.currency_code || ""} ${product.current_price}`} />
              <InfoTile label="原价参考" value={product.original_price == null ? "待补充" : `${product.currency_code || ""} ${product.original_price}`} />
              <InfoTile label="用户评分" value={product.rating == null ? "待补充" : String(product.rating)} />
              <InfoTile label="评价数量" value={String(product.review_count || 0)} />
            </div>
            {safeSourceUrl ? (
              <Button asChild variant="outline">
                <Link href={safeSourceUrl} target="_blank">打开原始商品链接</Link>
              </Button>
            ) : null}
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-6 xl:grid-cols-3">
        <Card className="border-white/8 bg-[#121c2c] xl:col-span-2">
          <CardHeader>
            <CardTitle>为什么这个商品值得继续看</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-3">
            <InsightBlock title="市场发现能力" value={analysis?.core_keywords?.length ? analysis.core_keywords.join(" / ") : "先去市场分析页生成真实趋势判断。"} />
            <InsightBlock title="利润预测能力" value={intelligence?.profit_estimate || "利润空间还没生成，先补跑分析。"} />
            <InsightBlock title="供应链推荐能力" value={analysis?.sourcing_keywords?.length ? analysis.sourcing_keywords.join(" / ") : "下一步去供应方案页看更合适的货源。"} />
          </CardContent>
        </Card>

        <Card className="border-white/8 bg-[#121c2c]">
          <CardHeader>
            <CardTitle>下一步最该做什么</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <NextStep title="先看趋势判断" desc="先看需求、趋势和进入难度，再决定要不要继续。"/>
            <NextStep title="再看采购方案" desc="看价格、MOQ、风险和供应稳定性。"/>
            <NextStep title="最后看 AI 建议" desc="把市场、利润、供应放到一起看结论。"/>
          </CardContent>
        </Card>
      </div>

      <Card className="border-white/8 bg-[#121c2c]">
        <CardHeader>
          <CardTitle>商品图片与素材参考</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            {productImages.length ? (
              productImages.map((image) => (
                // eslint-disable-next-line @next/next/no-img-element
                <img key={image.id} src={image.image_url} alt={product.title} className="h-52 w-full rounded-2xl border border-white/8 object-cover" />
              ))
            ) : (
              <EmptyState text={lang === "en" ? "No images yet." : "当前没有图片。"} />
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function InsightBlock({ title, value }: { title: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/8 bg-white/5 p-4">
      <div className="text-base font-semibold text-white">{title}</div>
      <div className="mt-2 text-sm leading-7 text-white/60">{value}</div>
    </div>
  );
}

function NextStep({ title, desc }: { title: string; desc: string }) {
  return (
    <div className="rounded-2xl border border-white/8 bg-white/5 p-4">
      <div className="text-sm font-semibold text-white">{title}</div>
      <div className="mt-2 text-sm leading-7 text-white/60">{desc}</div>
    </div>
  );
}

function toRecommendationLabel(value?: string) {
  if (value === "sell") return "值得继续推进";
  if (value === "monitor") return "建议继续观察";
  if (value === "ignore") return "暂时不建议进入";
  return "待生成";
}

function toCompetitionLabel(value?: string) {
  if (value === "low") return "竞争压力较低";
  if (value === "medium") return "竞争压力中等";
  if (value === "high") return "竞争压力较高";
  return "待生成";
}

function toSafeHttpUrl(value?: string | null) {
  if (!value) return null;
  try {
    const parsed = new URL(value);
    if (parsed.protocol === "http:" || parsed.protocol === "https:") return value;
    return null;
  } catch {
    return null;
  }
}
