"use client";

import { useState } from "react";
import { ExternalLink, Loader2, Search } from "lucide-react";

import { Badge, Button, Card, CardContent, CardHeader, CardTitle, EmptyState, Input, InfoTile, StatusBadge, Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/design-system/components";
import { matchSuppliers } from "@/lib/api";
import { getToken } from "@/lib/auth";
import { Language, t } from "@/lib/i18n";
import type { SupplierMatchItem } from "@/lib/types";

export function SupplierCenter({ lang }: { lang: Language }) {
  const text = t(lang);
  const [keyword, setKeyword] = useState("air fryer");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [items, setItems] = useState<SupplierMatchItem[]>([]);

  async function handleSearch() {
    if (!keyword.trim()) return;
    setLoading(true);
    setError("");
    try {
      const result = await matchSuppliers(keyword.trim(), getToken());
      setItems(result.suppliers);
    } catch (err) {
      setError(err instanceof Error ? err.message : text.supplierSearchFailed);
      setItems([]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-5">
      <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
        <CardHeader>
          <CardTitle>{text.supplierPageTitle}</CardTitle>
          <p className="text-sm text-white/55">{text.supplierPageDesc}</p>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-3">
            <div className="relative flex-1">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-white/35" />
              <Input value={keyword} onChange={(event) => setKeyword(event.target.value)} className="pl-9" placeholder={text.supplierKeywordPlaceholder} />
            </div>
            <Button type="button" onClick={handleSearch} disabled={loading}>
              {loading ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />{text.supplierMatching}</> : text.supplierStartMatch}
            </Button>
          </div>
          {error ? <div className="rounded-2xl border border-rose-400/20 bg-rose-400/10 px-4 py-3 text-sm text-rose-200">{error}</div> : null}
        </CardContent>
      </Card>

      <div className="grid gap-5 xl:grid-cols-[1.1fr_0.9fr]">
        <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <CardHeader>
            <CardTitle>推荐供应商</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {items.length ? items.map((item, index) => (
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
            )) : <EmptyState text={text.supplierEmpty} />}
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
                  {items.map((item, index) => (
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
              {[...items].sort((a, b) => b.match_score - a.match_score).slice(0, 5).map((item, index) => (
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
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
