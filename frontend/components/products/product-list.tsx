"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useMemo, useState } from "react";
import { Search, Trash2 } from "lucide-react";

import { ROUTES, productDetailRoute } from "@/config/routes";
import { Badge, Button, Card, CardContent, CardHeader, EmptyState, Input, StatusBadge } from "@/design-system/components";
import { batchDeleteProducts, deleteProduct } from "@/lib/api";
import { getToken } from "@/lib/auth";
import { Language, t } from "@/lib/i18n";
import { Product } from "@/lib/types";
import { ProductIntelligenceBadge } from "@/components/products/product-intelligence-badge";

export function ProductList({ products, total, lang }: { products: Product[]; total: number; lang: Language }) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [search, setSearch] = useState(searchParams.get("search") || "");
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [batchDeleting, setBatchDeleting] = useState(false);
  const text = t(lang);
  const allVisibleIds = useMemo(() => products.map((product) => product.id), [products]);
  const allSelected = products.length > 0 && selectedIds.length === products.length;
  const selectedCount = selectedIds.length;

  async function handleDelete(id: number) {
    const ok = window.confirm(text.confirmDelete);
    if (!ok) return;
    await deleteProduct(id, getToken());
    setSelectedIds((current) => current.filter((item) => item !== id));
    router.refresh();
  }

  async function handleBatchDelete() {
    if (!selectedIds.length) return;
    const ok = window.confirm(text.confirmBatchDelete);
    if (!ok) return;
    setBatchDeleting(true);
    try {
      await batchDeleteProducts(selectedIds, getToken());
      setSelectedIds([]);
      router.refresh();
    } finally {
      setBatchDeleting(false);
    }
  }

  function toggleSelected(id: number) {
    setSelectedIds((current) => (current.includes(id) ? current.filter((item) => item !== id) : [...current, id]));
  }

  function toggleSelectAll() {
    setSelectedIds((current) => (current.length === products.length ? [] : allVisibleIds));
  }

  function handleSearchSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const params = new URLSearchParams(searchParams.toString());
    if (search.trim()) {
      params.set("search", search.trim());
    } else {
      params.delete("search");
    }
    const query = params.toString();
    router.push(query ? `${ROUTES.products}?${query}` : ROUTES.products);
  }

  return (
    <Card className="overflow-hidden">
      <CardHeader className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
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
          <Badge variant={selectedCount ? "warning" : "neutral"} className="px-4 py-2 text-sm text-app-text-secondary">
            {text.productListSelection.replace("{count}", String(selectedCount))}
          </Badge>
        </div>
        <div className="mb-5 flex flex-wrap items-center gap-3">
          <label className="inline-flex cursor-pointer items-center gap-2 rounded-full border border-app-border bg-white/6 px-4 py-2 text-sm text-app-text-secondary transition hover:bg-white/8 hover:text-white">
            <input
              type="checkbox"
              checked={allSelected}
              onChange={toggleSelectAll}
              className="h-4 w-4 rounded border border-white/25 bg-transparent accent-[#6C5CE7]"
            />
            <span>{text.selectAll}</span>
          </label>
          <Button type="button" variant="danger" onClick={handleBatchDelete} disabled={!selectedCount || batchDeleting}>
            {batchDeleting ? (
              text.deleting
            ) : (
              <>
                <Trash2 className="mr-2 h-4 w-4" />
                {text.batchDelete}
              </>
            )}
          </Button>
        </div>
        <div className="space-y-4">
          {products.map((product) => (
            <Card
              key={product.id}
              variant="subtle"
              className={`p-4 transition hover:-translate-y-0.5 hover:border-app-border-strong hover:bg-white/8 ${selectedIds.includes(product.id) ? "border-app-border-strong bg-white/10 shadow-app-soft" : ""}`}
            >
              <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                <div className="flex gap-4">
                  <label className="mt-1 inline-flex cursor-pointer items-center">
                    <input
                      type="checkbox"
                      checked={selectedIds.includes(product.id)}
                      onChange={() => toggleSelected(product.id)}
                      className="h-4 w-4 rounded border border-white/25 bg-transparent accent-[#6C5CE7]"
                    />
                  </label>
                  {product.images?.[0]?.image_url ? (
                    <img src={product.images[0].image_url} alt={product.title} className="h-24 w-24 rounded-2xl border border-app-border object-cover shadow-app-soft" />
                  ) : (
                    <div className="h-24 w-24 rounded-2xl border border-app-border bg-white/5" />
                  )}
                  <div className="space-y-2">
                    <div className="flex flex-wrap gap-2">
                      <Badge variant="blue">{text.productId}{product.id}</Badge>
                      <StatusBadge status={product.is_active ? "success" : "warning"} label={product.is_active ? text.active : text.inactive} />
                      <ProductIntelligenceBadge productId={product.id} lang={lang} />
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
                    <Link href={productDetailRoute(product.id)}>{text.viewDetail}</Link>
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
