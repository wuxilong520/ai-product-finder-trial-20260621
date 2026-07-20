"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useMemo, useState } from "react";
import { ArrowUpRight, Search, Sparkles, Trash2 } from "lucide-react";

import { ROUTES, productDetailRoute } from "@/config/routes";
import { Badge, Button, Card, CardContent, EmptyState, InfoTile, Input } from "@/design-system/components";
import { batchDeleteProducts, deleteProduct } from "@/lib/api-gateway";
import { getToken } from "@/lib/auth";
import { Language } from "@/lib/i18n";
import { Product } from "@/lib/types";

export function ProductList({ products, total, lang }: { products: Product[]; total: number; lang: Language }) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [search, setSearch] = useState(searchParams.get("search") || "");
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [batchDeleting, setBatchDeleting] = useState(false);
  const [sortBy, setSortBy] = useState<"latest" | "reviews" | "rating">("latest");

  const sortedProducts = useMemo(() => {
    const nextProducts = [...products];
    if (sortBy === "reviews") {
      return nextProducts.sort((left, right) => Number(right.review_count || 0) - Number(left.review_count || 0));
    }
    if (sortBy === "rating") {
      return nextProducts.sort((left, right) => Number(right.rating || 0) - Number(left.rating || 0));
    }
    return nextProducts.sort((left, right) => new Date(right.created_at).getTime() - new Date(left.created_at).getTime());
  }, [products, sortBy]);

  async function handleDelete(id: number) {
    const accepted = window.confirm("确认删除这个商品吗？");
    if (!accepted) return;
    await deleteProduct(id, getToken());
    setSelectedIds((current) => current.filter((item) => item !== id));
    router.refresh();
  }

  async function handleBatchDelete() {
    if (!selectedIds.length) return;
    const accepted = window.confirm("确认删除已选商品吗？");
    if (!accepted) return;
    setBatchDeleting(true);
    try {
      await batchDeleteProducts(selectedIds, getToken());
      setSelectedIds([]);
      router.refresh();
    } finally {
      setBatchDeleting(false);
    }
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

  function toggleSelected(id: number) {
    setSelectedIds((current) => current.includes(id) ? current.filter((item) => item !== id) : [...current, id]);
  }

  return (
    <div className="space-y-6">
      <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
        <CardContent className="space-y-5 p-6">
          <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
            <div>
              <div className="text-lg font-semibold text-white">商品机会榜单</div>
              <div className="mt-2 text-sm leading-7 text-white/58">
                用榜单方式看真实商品，优先挑出更值得继续看、继续比货、继续做 AI 判断的机会。
              </div>
            </div>
            <form onSubmit={handleSearchSubmit} className="flex w-full max-w-xl gap-3">
              <div className="relative flex-1">
                <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-white/35" />
                <Input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="搜索商品标题或关键词" className="pl-9" />
              </div>
              <Button type="submit">搜索</Button>
            </form>
          </div>

          <div className="grid gap-4 md:grid-cols-4">
            <InfoTile label="当前商品总量" value={`${total}`} />
            <InfoTile label="已选商品" value={`${selectedIds.length}`} />
            <InfoTile label="当前排序" value={sortLabel(sortBy)} />
            <InfoTile label="当前目标" value="挑出更值得继续分析的商品" />
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {[
              { key: "latest", label: "最新进入" },
              { key: "reviews", label: "评价最多" },
              { key: "rating", label: "评分最高" },
            ].map((item) => (
              <button
                key={item.key}
                type="button"
                onClick={() => setSortBy(item.key as "latest" | "reviews" | "rating")}
                className={`rounded-full border px-4 py-2 text-sm transition ${
                  sortBy === item.key ? "border-[#4F7CFF]/24 bg-[#4F7CFF]/10 text-[#9CC0FF]" : "border-white/10 bg-white/5 text-white/70 hover:bg-white/10"
                }`}
              >
                {item.label}
              </button>
            ))}
            <Button type="button" variant="danger" onClick={handleBatchDelete} disabled={!selectedIds.length || batchDeleting}>
              {batchDeleting ? "删除中..." : <><Trash2 className="mr-2 h-4 w-4" />删除已选</>}
            </Button>
          </div>
        </CardContent>
      </Card>

      {sortedProducts.length ? (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {sortedProducts.map((product, index) => (
            <Card key={product.id} className="border-white/8 bg-[#121c2c] transition hover:-translate-y-0.5 hover:border-white/14 hover:bg-[#16233a]">
              <CardContent className="space-y-4 p-5">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-3">
                    <input
                      type="checkbox"
                      checked={selectedIds.includes(product.id)}
                      onChange={() => toggleSelected(product.id)}
                      className="mt-1 h-4 w-4 rounded border border-white/25 bg-transparent accent-[#6C5CE7]"
                    />
                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <Badge variant="brand">TOP {index + 1}</Badge>
                        <Badge variant="neutral">{product.is_active ? "已启用" : "未启用"}</Badge>
                      </div>
                      <div className="mt-3 text-lg font-semibold text-white">{product.title_zh || product.title}</div>
                      <div className="mt-1 text-sm text-white/48">{product.title}</div>
                    </div>
                  </div>
                  {product.images?.[0]?.image_url ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img src={product.images[0].image_url} alt={product.title} className="h-20 w-20 rounded-2xl border border-white/8 object-cover" />
                  ) : (
                    <div className="h-20 w-20 rounded-2xl border border-white/8 bg-white/5" />
                  )}
                </div>

                <div className="grid gap-3 md:grid-cols-2">
                  <InfoTile label="当前价格" value={product.current_price == null ? "待补充" : `${product.currency_code || ""} ${product.current_price}`} />
                  <InfoTile label="用户评分" value={product.rating == null ? "待补充" : String(product.rating)} />
                  <InfoTile label="评价数量" value={String(product.review_count || 0)} />
                  <InfoTile label="进入时间" value={formatDate(product.created_at)} />
                </div>

                <div className="rounded-2xl border border-white/8 bg-black/10 p-4 text-sm leading-7 text-white/65">
                  这条商品已经进入系统，下一步建议先看详情页里的 AI 商业报告，再决定要不要继续做采购方案。
                </div>

                <div className="flex flex-wrap gap-3">
                  <Button asChild>
                    <Link href={productDetailRoute(product.id)}>
                      查看详情
                      <ArrowUpRight className="ml-2 h-4 w-4" />
                    </Link>
                  </Button>
                  <Button asChild variant="secondary">
                    <Link href={`${ROUTES.insights}?keyword=${encodeURIComponent(product.title_zh || product.title)}`}>
                      <Sparkles className="mr-2 h-4 w-4" />
                      看市场分析
                    </Link>
                  </Button>
                  <Button type="button" variant="danger" onClick={() => void handleDelete(product.id)}>
                    删除
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card className="border-white/8 bg-[#121c2c]">
          <CardContent className="py-10">
            <EmptyState text={lang === "en" ? "No real products yet." : "当前还没有真实商品。"} />
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function sortLabel(sortBy: "latest" | "reviews" | "rating") {
  if (sortBy === "reviews") return "评价最多";
  if (sortBy === "rating") return "评分最高";
  return "最新进入";
}

function formatDate(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "时间待补充";
  return `${date.getMonth() + 1}/${date.getDate()}`;
}
