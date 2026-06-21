"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";
import { Search, Sparkles } from "lucide-react";

import { Badge, Button, Card, CardContent, CardDescription, CardHeader, CardTitle, EmptyState, Input, StatusBadge } from "@/design-system/components";
import { deleteProduct } from "@/lib/api";
import { getToken } from "@/lib/auth";
import { Language, t } from "@/lib/i18n";
import { Product } from "@/lib/types";

export function ProductList({ products, total, lang }: { products: Product[]; total: number; lang: Language }) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [search, setSearch] = useState(searchParams.get("search") || "");
  const text = t(lang);

  async function handleDelete(id: number) {
    const ok = window.confirm(text.confirmDelete);
    if (!ok) return;
    await deleteProduct(id, getToken());
    router.refresh();
  }

  function handleSearchSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const params = new URLSearchParams(searchParams.toString());
    if (search.trim()) {
      params.set("search", search.trim());
    } else {
      params.delete("search");
    }
    router.push(`/dashboard?${params.toString()}`);
  }

  return (
    <Card className="overflow-hidden">
      <CardHeader className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <CardTitle>{text.productListTitle}</CardTitle>
          <CardDescription>{text.productListDesc.replace("{count}", String(total))}</CardDescription>
        </div>
        <form onSubmit={handleSearchSubmit} className="flex w-full max-w-sm gap-2">
          <div className="relative flex-1">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-app-text-muted" />
            <Input value={search} onChange={(e) => setSearch(e.target.value)} placeholder={text.productSearchPlaceholder} className="pl-9" />
          </div>
          <Button type="submit" variant="outline">
            {text.search}
          </Button>
        </form>
      </CardHeader>
      <CardContent>
        <div className="mb-5 flex flex-wrap gap-3">
          <Badge variant="brand" className="px-4 py-2 text-sm font-medium">{text.productZone}</Badge>
          <Badge variant="neutral" className="px-4 py-2 text-sm text-app-text-secondary">
            <Sparkles className="h-4 w-4 text-app-brand-secondary" />
            {text.unifiedStyle}
          </Badge>
        </div>
        <div className="space-y-4">
          {products.map((product) => (
            <Card key={product.id} variant="subtle" className="p-4 transition hover:-translate-y-0.5 hover:border-app-border-strong hover:bg-white/8">
              <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                <div className="flex gap-4">
                  {product.images?.[0]?.image_url ? (
                    <img src={product.images[0].image_url} alt={product.title} className="h-24 w-24 rounded-2xl border border-app-border object-cover shadow-app-soft" />
                  ) : (
                    <div className="h-24 w-24 rounded-2xl border border-app-border bg-white/5" />
                  )}
                  <div className="space-y-2">
                    <div className="flex flex-wrap gap-2">
                      <Badge variant="blue">{text.productId}{product.id}</Badge>
                      <StatusBadge status={product.is_active ? "success" : "warning"} label={product.is_active ? text.active : text.inactive} />
                    </div>
                    <h3 className="text-lg font-semibold text-white">{product.title}</h3>
                    <p className="text-sm text-app-text-muted">{product.title_zh || text.noTranslation}</p>
                    <div className="flex flex-wrap gap-4 text-sm text-app-text-secondary">
                      <span>{text.price}：{product.current_price ?? "—"}</span>
                      <span>{text.rating}：{product.rating ?? "—"}</span>
                      <span>{text.reviews}：{product.review_count ?? 0}</span>
                    </div>
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button asChild variant="outline">
                    <Link href={`/products/${product.id}`}>{text.viewDetail}</Link>
                  </Button>
                  <Button variant="danger" onClick={() => handleDelete(product.id)}>
                    {text.delete}
                  </Button>
                </div>
              </div>
            </Card>
          ))}

          {products.length === 0 ? (
            <EmptyState text={text.noProducts} />
          ) : null}
        </div>
      </CardContent>
    </Card>
  );
}
