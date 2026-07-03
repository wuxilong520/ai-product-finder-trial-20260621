"use client";

import { useEffect, useMemo, useState } from "react";
import { ExternalLink, Loader2, Search } from "lucide-react";

import { Badge, Button, Card, CardContent, CardHeader, CardTitle, EmptyState, Input, InfoTile, StatusBadge, Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/design-system/components";
import { ROUTES } from "@/config/routes";
import { matchSuppliers } from "@/lib/api-gateway";
import { getToken } from "@/lib/auth";
import { Language, t } from "@/lib/i18n";
import type { SupplierMatchItem } from "@/lib/types";
import Link from "next/link";

export function SupplierCenter({
  lang,
  initialKeyword,
  initialCategory,
}: {
  lang: Language;
  initialKeyword?: string;
  initialCategory?: string;
}) {
  const text = t(lang);
  const [keyword, setKeyword] = useState(initialKeyword || "air fryer");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [items, setItems] = useState<SupplierMatchItem[]>([]);
  const [maxPrice, setMaxPrice] = useState("");
  const [minScore, setMinScore] = useState("0");
  const [availableOnly, setAvailableOnly] = useState(true);

  async function handleSearch(targetKeyword?: string) {
    const finalKeyword = (targetKeyword || keyword).trim();
    if (!finalKeyword) return;
    setLoading(true);
    setError("");
    try {
      const result = await matchSuppliers(finalKeyword, getToken());
      setItems(result.suppliers);
    } catch (err) {
      setError(err instanceof Error ? err.message : text.supplierSearchFailed);
      setItems([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!initialKeyword?.trim()) return;
    void handleSearch(initialKeyword);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialKeyword]);

  const filteredItems = useMemo(() => {
    const priceLimit = maxPrice ? Number(maxPrice) : null;
    const scoreFloor = Number(minScore || 0);
    return items.filter((item) => {
      if (availableOnly && !/available|instock|ready|现货|有货/i.test(item.availability || "")) {
        return false;
      }
      if (!Number.isNaN(scoreFloor) && item.match_score < scoreFloor) {
        return false;
      }
      if (priceLimit !== null && !Number.isNaN(priceLimit) && item.supplier_price != null && item.supplier_price > priceLimit) {
        return false;
      }
      return true;
    });
  }, [availableOnly, items, maxPrice, minScore]);

  return (
    <div className="space-y-5">
      <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
        <CardHeader>
          <CardTitle>供应链匹配页</CardTitle>
          <p className="text-sm text-white/55">
            这一步就是把你选中的商品，继续往 1688 这类供货入口去匹配。你先筛价格、匹配分、是否有货，再决定要不要进入利润决策和半自动上架。
          </p>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-3 md:grid-cols-3">
            <InfoTile label="当前类目" value={initialCategory || "未指定"} />
            <InfoTile label="当前商品" value={keyword || "未指定"} />
            <InfoTile label="当前阶段" value="筛供应链" />
          </div>
          <div className="flex gap-3">
            <div className="relative flex-1">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-white/35" />
              <Input value={keyword} onChange={(event) => setKeyword(event.target.value)} className="pl-9" placeholder={text.supplierKeywordPlaceholder} />
            </div>
            <Button type="button" onClick={() => void handleSearch()} disabled={loading}>
              {loading ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />{text.supplierMatching}</> : text.supplierStartMatch}
            </Button>
          </div>
          <div className="grid gap-3 md:grid-cols-3">
            <Input value={maxPrice} onChange={(event) => setMaxPrice(event.target.value)} placeholder="最高价格，例如 30" />
            <Input value={minScore} onChange={(event) => setMinScore(event.target.value)} placeholder="最低匹配分，例如 60" />
            <label className="flex h-12 items-center gap-3 rounded-2xl border border-white/10 bg-white/5 px-4 text-sm text-white">
              <input
                type="checkbox"
                checked={availableOnly}
                onChange={(event) => setAvailableOnly(event.target.checked)}
                className="h-4 w-4"
              />
              只看当前显示为可供货
            </label>
          </div>
          <div className="rounded-2xl border border-[#4F7CFF]/20 bg-[#4F7CFF]/10 px-4 py-3 text-sm leading-7 text-[#D8E3FF]">
            当前这页能真实筛的是：关键词、价格、匹配分、是否有货。供应商评分、MOQ、真实工厂认证这几个字段，现在后端还没有完整返回，所以我不假装已经接通了。
          </div>
          {error ? <div className="rounded-2xl border border-rose-400/20 bg-rose-400/10 px-4 py-3 text-sm text-rose-200">{error}</div> : null}
        </CardContent>
      </Card>

      <div className="grid gap-5 xl:grid-cols-[1.1fr_0.9fr]">
        <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <CardHeader>
            <CardTitle>筛选后的供应商结果</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {filteredItems.length ? filteredItems.map((item, index) => (
              <a key={`${item.platform}-${item.supplier_url}-${index}`} href={item.supplier_url} target="_blank" rel="noreferrer" className="block rounded-[18px] border border-white/8 bg-white/[0.03] p-4 transition hover:bg-white/[0.06]">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge variant="brand">{item.platform}</Badge>
                    <StatusBadge status={item.match_score >= 70 ? "success" : item.match_score >= 45 ? "warning" : "blocked"} label={`${text.supplierMatchScore} ${Math.round(item.match_score)}`} />
                  </div>
                  <div className="inline-flex items-center gap-2 text-sm text-[#7dd3fc]">
                    <ExternalLink className="h-4 w-4" />
                    {text.supplierOpen}
                  </div>
                </div>
                <div className="mt-4 text-base font-medium text-white">{item.supplier_title}</div>
                <div className="mt-1 text-sm text-white/45">{item.platform} · {item.supplier_name || "供应入口已就绪"}</div>
                <div className="mt-4 grid gap-4 md:grid-cols-3">
                  <InfoTile label={text.supplierPrice} value={item.supplier_price != null ? `${item.currency || ""} ${Number(item.supplier_price).toFixed(2)}` : text.supplierPending} />
                  <InfoTile label="成本空间" value={item.supplier_price != null ? `${Math.max(0, 100 - Math.round(item.supplier_price)).toString()}%` : "待核算"} />
                  <InfoTile label={text.supplierStatus} value={item.availability} />
                </div>
              </a>
            )) : <EmptyState text={items.length ? "当前筛选条件下没有结果，你可以放宽价格或匹配分。" : text.supplierEmpty} />}
          </CardContent>
        </Card>

        <div className="space-y-5">
          <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <CardTitle>报价对比</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <tr>
                    <TableHead>{text.supplierPlatform}</TableHead>
                    <TableHead>{text.title}</TableHead>
                    <TableHead>{text.supplierPrice}</TableHead>
                    <TableHead>{text.supplierMatchScore}</TableHead>
                  </tr>
                </TableHeader>
                <TableBody>
                  {filteredItems.map((item, index) => (
                    <TableRow key={`table-${item.platform}-${index}`}>
                      <TableCell>{item.platform}</TableCell>
                      <TableCell>{item.supplier_title}</TableCell>
                      <TableCell>{item.supplier_price != null ? `${item.currency || ""} ${Number(item.supplier_price).toFixed(2)}` : text.supplierPending}</TableCell>
                      <TableCell>{Math.round(item.match_score)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <CardTitle>优先合作顺序</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {[...filteredItems].sort((a, b) => b.match_score - a.match_score).slice(0, 5).map((item, index) => (
                <div key={`rank-${item.platform}-${index}`} className="flex items-center justify-between rounded-[16px] border border-white/8 bg-white/[0.03] px-4 py-3">
                  <div>
                    <div className="text-sm font-medium text-white">TOP {index + 1} · {item.platform}</div>
                    <div className="mt-1 text-xs text-white/45">{item.supplier_title}</div>
                  </div>
                  <Badge variant={item.match_score >= 70 ? "success" : item.match_score >= 45 ? "warning" : "neutral"} className="px-3 py-1.5 text-sm">
                    {Math.round(item.match_score)}
                  </Badge>
                </div>
              ))}
              <Link
                href={`${ROUTES.actionProfit}${keyword ? `?keyword=${encodeURIComponent(keyword)}` : ""}`}
                className="block rounded-[16px] border border-[#4F7CFF]/20 bg-[#4F7CFF]/10 px-4 py-4 text-sm font-medium text-[#D8E3FF] transition hover:bg-[#4F7CFF]/16"
              >
                这一步筛完后，进入利润决策 + 半自动上架准备
              </Link>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
