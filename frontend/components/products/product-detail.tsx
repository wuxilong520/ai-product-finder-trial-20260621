import Link from "next/link";

import { Badge, Button, Card, CardContent, CardHeader, CardTitle, EmptyState, InfoTile, LinkTile, StatusBadge, TagList } from "@/design-system/components";
import { Language, t } from "@/lib/i18n";
import { AnalyzeResponse, Product } from "@/lib/types";
import { DecisionCard } from "@/components/decision/decision-card";
import { ProductIntelligencePanel } from "@/components/products/product-intelligence-panel";
import { BusinessTruthCard } from "@/components/dashboard/business-truth-card";

export function ProductDetail({
  product,
  analysisReport,
  lang,
}: {
  product: Product;
  analysisReport?: AnalyzeResponse | null;
  lang: Language;
}) {
  const intelligence = analysisReport?.intelligence;
  const analysis = analysisReport?.analysis;
  const recommendationMeta = intelligence ? getRecommendationMeta(intelligence.recommendation, lang) : null;
  const text = t(lang);

  return (
    <div className="space-y-6">
      <Card className="section-card">
        <CardHeader className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
          <div>
            <div className="mb-3 flex flex-wrap gap-2">
              <Badge variant="blue">{text.productId}{product.id}</Badge>
              <StatusBadge status={product.is_active ? "success" : "warning"} label={product.is_active ? text.active : text.inactive} />
            </div>
            <CardTitle>{product.title}</CardTitle>
            <p className="mt-2 text-app-text-secondary">{product.title_zh || text.noTranslation}</p>
          </div>
          <Button asChild variant="outline">
            <Link href={product.source_url} target="_blank">
              {text.detailOpenSource}
            </Link>
          </Button>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <InfoTile label={text.price} value={product.current_price ? `${product.currency_code || ""} ${product.current_price}` : "—"} />
            <InfoTile label={text.originalPrice} value={product.original_price ? `${product.currency_code || ""} ${product.original_price}` : "—"} />
            <InfoTile label={`${text.rating} / ${text.reviews}`} value={`${product.rating ?? "—"} / ${product.review_count ?? 0}`} />
          </div>
        </CardContent>
      </Card>

      {intelligence ? (
        <Card>
          <CardHeader>
            <CardTitle>{text.detailDecision}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="inline-flex rounded-full px-4 py-2 text-sm font-semibold text-white" style={{ background: recommendationMeta?.color }}>
                {recommendationMeta?.label}
              </div>
              <div className="grid gap-4 md:grid-cols-4">
                <InfoTile label={text.detailScore} value={`${intelligence.product_score} / 100`} />
                <InfoTile label={text.detailRecommendation} value={toRecommendationLabel(intelligence.recommendation, lang)} />
                <InfoTile label={text.detailCompetition} value={toCompetitionLabel(intelligence.competition_level, lang)} />
                <InfoTile label={text.detailPotential} value={toPotentialLabel(intelligence.selling_potential, lang)} />
              </div>
              <InfoTile label={text.detailProfit} value={intelligence.profit_estimate} />
              <div className="rounded-2xl border border-app-border bg-white/5 p-4 shadow-app-soft">
                <p className="text-sm text-app-text-muted">{text.detailReason}</p>
                <div className="mt-3 space-y-2">
                  {intelligence.reason.map((item) => (
                    <p key={item} className="text-sm text-app-text-secondary">
                      - {item}
                    </p>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      ) : null}

      {analysis ? (
        <Card>
          <CardHeader>
            <CardTitle>{text.detailSummary}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-5">
              <div>
                <p className="text-sm text-app-text-muted">{text.detailTitleZh}</p>
                <p className="mt-1 text-base font-semibold text-white">{analysis.title_zh}</p>
              </div>
              <TagGroup title={text.detailKeywords} items={analysis.core_keywords} lang={lang} />
              <TagGroup title={text.detailSellingPoints} items={analysis.selling_points} lang={lang} />
              <TagGroup title={text.detailSourcingKeywords} items={analysis.sourcing_keywords} lang={lang} />
              <div>
                <p className="text-sm text-app-text-muted">{text.detailSourceLinks}</p>
                <div className="mt-2 flex flex-col gap-2">
                  <LinkTile href={analysis.source_links["1688_url"]} label={text.open1688} />
                  <LinkTile href={analysis.source_links["pdd_url"]} label={text.openPdd} />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      ) : null}

      <div className="grid gap-6 xl:grid-cols-2">
        <ProductIntelligencePanel productId={product.id} lang={lang} />
        <DecisionCard productId={product.id} lang={lang} />
      </div>
      <BusinessTruthCard productId={product.id} lang={lang} />

      <Card>
        <CardHeader>
          <CardTitle>{text.detailImages}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            {product.images.length > 0 ? (
              product.images.map((image) => (
                <img key={image.id} src={image.image_url} alt={product.title} className="h-52 w-full rounded-2xl border border-app-border object-cover shadow-app-soft" />
              ))
            ) : (
              <EmptyState text={text.noImages} />
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function TagGroup({ title, items, lang }: { title: string; items: string[]; lang: Language }) {
  const text = t(lang);
  return (
    <div>
      <p className="text-sm text-app-text-muted">{title}</p>
      <div className="mt-2">
        <TagList items={items} emptyText={text.emptyState} />
      </div>
    </div>
  );
}

function toRecommendationLabel(value: "sell" | "monitor" | "ignore", lang: Language) {
  const text = t(lang);
  if (value === "sell") return text.productRecSell;
  if (value === "monitor") return text.productRecMonitor;
  return text.productRecIgnore;
}

function toCompetitionLabel(value: "low" | "medium" | "high", lang: Language) {
  const text = t(lang);
  if (value === "low") return text.productCompetitionLow;
  if (value === "medium") return text.productCompetitionMedium;
  return text.productCompetitionHigh;
}

function toPotentialLabel(value: "weak" | "ok" | "strong", lang: Language) {
  const text = t(lang);
  if (value === "strong") return text.productPotentialStrong;
  if (value === "ok") return text.productPotentialOk;
  return text.productPotentialWeak;
}

function getRecommendationMeta(value: "sell" | "monitor" | "ignore", lang: Language) {
  const text = t(lang);
  if (value === "sell") {
    return { label: text.productMetaSell, color: "linear-gradient(90deg, #34d399, #10b981)" };
  }
  if (value === "monitor") {
    return { label: text.productMetaMonitor, color: "linear-gradient(90deg, #fbbf24, #f59e0b)" };
  }
  return { label: text.productMetaIgnore, color: "linear-gradient(90deg, #fb7185, #ef4444)" };
}
