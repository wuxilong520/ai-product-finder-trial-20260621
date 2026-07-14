"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { Heart, Loader2, Scale, Search, Sparkles } from "lucide-react";

import { Badge, Button, Card, CardContent, CardHeader, CardTitle, EmptyState, InfoTile, Input } from "@/design-system/components";
import { ROUTES } from "@/config/routes";
import { analyzeProcurementItem, favoriteProcurementItem, getProcurementPool } from "@/lib/api-gateway";
import { getToken } from "@/lib/auth";
import { Language } from "@/lib/i18n";
import type { ProcurementPoolItem } from "@/lib/types";


export function ProcurementCenter({
  lang,
  initialKeyword,
}: {
  lang: Language;
  initialKeyword?: string;
}) {
  void lang;
  const [keyword, setKeyword] = useState(initialKeyword || "wireless earbuds");
  const [sort, setSort] = useState("latest");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [items, setItems] = useState<ProcurementPoolItem[]>([]);
  const [analyzingId, setAnalyzingId] = useState<number | null>(null);
  const [selected, setSelected] = useState<number[]>([]);
  const [maxPrice, setMaxPrice] = useState("");
  const [minProfit, setMinProfit] = useState("");
  const [minSupplierScore, setMinSupplierScore] = useState("");
  const [riskFilter, setRiskFilter] = useState("all");

  async function loadPool(targetKeyword?: string) {
    const finalKeyword = (targetKeyword || keyword).trim();
    if (!finalKeyword) return;
    setLoading(true);
    setError("");
    try {
      const result = await getProcurementPool({ keyword: finalKeyword, sort }, getToken());
      setItems(result.items);
    } catch (err) {
      setItems([]);
      setError(err instanceof Error ? err.message : "读取采购池失败");
    } finally {
      setLoading(false);
    }
  }

  async function handleAnalyze(id: number) {
    setAnalyzingId(id);
    setError("");
    try {
      await analyzeProcurementItem(id, getToken());
      await loadPool();
    } catch (err) {
      setError(err instanceof Error ? err.message : "AI分析失败");
    } finally {
      setAnalyzingId(null);
    }
  }

  async function handleFavorite(id: number) {
    setError("");
    try {
      await favoriteProcurementItem(id, "FAVORITE", getToken());
      await loadPool();
    } catch (err) {
      setError(err instanceof Error ? err.message : "收藏失败");
    }
  }

  function toggleCompare(id: number) {
    setSelected((current) => {
      if (current.includes(id)) return current.filter((item) => item !== id);
      if (current.length >= 5) return current;
      return [...current, id];
    });
  }

  const compareHref = useMemo(
    () => `${ROUTES.actionProcurementCompare}?ids=${selected.join(",")}`,
    [selected],
  );

  const filteredItems = useMemo(() => {
    const priceLimit = maxPrice ? Number(maxPrice) : null;
    const profitFloor = minProfit ? Number(minProfit) : null;
    const supplierFloor = minSupplierScore ? Number(minSupplierScore) : null;

    return items.filter((item) => {
      if (priceLimit != null && !Number.isNaN(priceLimit) && item.min_price > priceLimit) {
        return false;
      }
      if (profitFloor != null && !Number.isNaN(profitFloor) && item.estimated_profit < profitFloor) {
        return false;
      }
      if (supplierFloor != null && !Number.isNaN(supplierFloor) && item.supplier_score < supplierFloor) {
        return false;
      }
      if (riskFilter !== "all" && item.risk_level !== riskFilter) {
        return false;
      }
      return true;
    });
  }, [items, maxPrice, minProfit, minSupplierScore, riskFilter]);

  return (
    <div className="space-y-5">
      <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
        <CardHeader>
          <div className="text-xs uppercase tracking-[0.24em] text-white/40">商航AI · 采购池</div>
          <CardTitle>先把真实货源收进采购池，再由你自己决定要分析哪一个</CardTitle>
          <p className="text-sm text-white/55">
            这里不是AI替你下单。它只负责把真实导入的货源、供应商竞争情况、利润空间和风险放在一起，帮你少走弯路。
          </p>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-3 md:grid-cols-4">
            <InfoTile label="当前关键词" value={keyword || "未填写"} />
            <InfoTile label="当前商品数" value={`${filteredItems.length} / ${items.length} 个`} />
            <InfoTile label="比较池" value={`${selected.length}/5`} />
            <InfoTile label="当前排序" value={sortLabel(sort)} />
          </div>
          <div className="flex gap-3">
            <div className="relative flex-1">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-white/35" />
              <Input value={keyword} onChange={(event) => setKeyword(event.target.value)} className="pl-9" placeholder="输入你想采购的商品，例如 wireless earbuds" />
            </div>
            <Button type="button" onClick={() => void loadPool()} disabled={loading}>
              {loading ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />读取中...</> : "读取采购池"}
            </Button>
          </div>
          <div className="grid gap-3 md:grid-cols-5">
            {[
              ["latest", "最新"],
              ["lowest_price", "价格最低"],
              ["highest_profit", "利润最高"],
              ["highest_score", "评分最高"],
              ["lowest_risk", "风险最低"],
            ].map(([value, label]) => (
              <button
                key={value}
                type="button"
                onClick={() => setSort(value)}
                className={`rounded-2xl border px-4 py-3 text-sm transition ${sort === value ? "border-[#4F7CFF]/30 bg-[#4F7CFF]/12 text-[#D8E3FF]" : "border-white/10 bg-white/5 text-white/70 hover:bg-white/10"}`}
              >
                {label}
              </button>
            ))}
          </div>
          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
            <Input value={maxPrice} onChange={(event) => setMaxPrice(event.target.value)} placeholder="价格筛选：最高成本" />
            <Input value={minProfit} onChange={(event) => setMinProfit(event.target.value)} placeholder="利润筛选：最低利润" />
            <Input value={minSupplierScore} onChange={(event) => setMinSupplierScore(event.target.value)} placeholder="供应评分：最低分" />
            <select
              value={riskFilter}
              onChange={(event) => setRiskFilter(event.target.value)}
              className="h-11 rounded-2xl border border-white/10 bg-white/5 px-4 text-sm text-white outline-none transition focus:border-[#4F7CFF]/40"
            >
              <option value="all" className="bg-[#121c2c]">风险筛选：全部</option>
              <option value="low" className="bg-[#121c2c]">风险最低</option>
              <option value="medium" className="bg-[#121c2c]">中风险</option>
              <option value="high" className="bg-[#121c2c]">高风险</option>
            </select>
          </div>
          <div className="rounded-2xl border border-[#4F7CFF]/20 bg-[#4F7CFF]/10 px-4 py-3 text-sm leading-7 text-[#D8E3FF]">
            当前采购池只吃真实来源：现有供应链数据库 + 1688插件主动导入。没有后台偷偷爬1688，也没有伪造20个假商品来充数。
          </div>
          {error ? <div className="rounded-2xl border border-rose-400/20 bg-rose-400/10 px-4 py-3 text-sm text-rose-200">{error}</div> : null}
          <div className="flex flex-wrap gap-3">
            <Link href={ROUTES.actionSuppliers} className="rounded-2xl border border-white/10 bg-white/5 px-4 py-2 text-sm text-white/80 transition hover:bg-white/10">
              去供应链页生成1688连接码
            </Link>
            <Link href={compareHref} className={`rounded-2xl px-4 py-2 text-sm transition ${selected.length ? "border border-[#4F7CFF]/20 bg-[#4F7CFF]/10 text-[#D8E3FF]" : "pointer-events-none border border-white/10 bg-white/5 text-white/35"}`}>
              比较已选商品
            </Link>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-5 xl:grid-cols-2">
        {filteredItems.length ? filteredItems.map((item) => {
          const isSelected = selected.includes(item.id);
          return (
            <Card key={item.id} className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
              <CardHeader>
                <div className="flex items-start justify-between gap-3">
                  <div className="space-y-2">
                    <div className="flex flex-wrap gap-2">
                      <Badge variant="brand">{item.source_platform}</Badge>
                      <Badge variant={item.risk_level === "low" ? "success" : item.risk_level === "medium" ? "warning" : "error"}>
                        风险 {item.risk_level}
                      </Badge>
                      <Badge variant="neutral">{item.status}</Badge>
                    </div>
                    <CardTitle className="text-lg">{item.title}</CardTitle>
                    <p className="text-sm text-white/55">{item.keyword}</p>
                  </div>
                  {item.image ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img src={item.image} alt={item.title} className="h-20 w-20 rounded-2xl object-cover border border-white/8 bg-white/5" />
                  ) : null}
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-3 md:grid-cols-3">
                  <InfoTile label="供应商数量" value={`${item.supplier_count}`} />
                  <InfoTile label="最低采购价" value={formatMoney(item.min_price)} />
                  <InfoTile label="平均采购价" value={formatMoney(item.avg_price)} />
                </div>
                <div className="grid gap-3 md:grid-cols-3">
                  <InfoTile label="利润预估" value={formatMoney(item.estimated_profit)} />
                  <InfoTile label="市场分" value={`${item.market_score.toFixed(1)}`} />
                  <InfoTile label="供应商分" value={`${item.supplier_score.toFixed(1)}`} />
                </div>
                {item.suppliers?.length ? (
                  <div className="rounded-2xl border border-white/8 bg-black/10 p-4 text-sm text-white/72">
                    最强供应商：{item.suppliers[0].supplier_name} · 价格 {formatMoney(item.suppliers[0].price)} · 真实性 {item.suppliers[0].supplier_truth_score.toFixed(1)}
                  </div>
                ) : null}
                {item.analysis ? (
                  <div className="rounded-2xl border border-emerald-400/20 bg-emerald-400/10 p-4 text-sm text-emerald-100">
                    AI分析结果：{item.analysis.recommendation} · 综合分 {item.analysis.product_score.toFixed(1)} · {item.analysis.reason.join(" / ")}
                  </div>
                ) : (
                  <div className="rounded-2xl border border-white/8 bg-white/5 p-4 text-sm text-white/60">
                    还没跑AI分析。只有你点击“AI分析”后，系统才会对这个商品做市场、利润、风险综合判断。
                  </div>
                )}
                <div className="flex flex-wrap gap-3">
                  <Button type="button" variant="secondary" onClick={() => void handleFavorite(item.id)}>
                    <Heart className="mr-2 h-4 w-4" />
                    收藏
                  </Button>
                  <Button type="button" variant={isSelected ? "secondary" : "default"} onClick={() => toggleCompare(item.id)}>
                    <Scale className="mr-2 h-4 w-4" />
                    {isSelected ? "取消比较" : "加入比较"}
                  </Button>
                  <Button type="button" onClick={() => void handleAnalyze(item.id)} disabled={analyzingId === item.id}>
                    {analyzingId === item.id ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />分析中...</> : <><Sparkles className="mr-2 h-4 w-4" />AI分析</>}
                  </Button>
                </div>
              </CardContent>
            </Card>
          );
        }) : (
          <Card className="border-white/8 bg-[#121c2c] xl:col-span-2">
            <CardContent className="py-10">
              <EmptyState
                title={items.length ? "当前筛选后没有商品" : "当前还没有采购池商品"}
                text={items.length ? "你可以放宽价格、利润、供应评分或风险筛选条件。" : "先去1688插件导入，或者直接用关键词读取已有真实供应链数据。"}
              />
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}

function formatMoney(value: number) {
  if (!Number.isFinite(value)) return "¥0.00";
  return `¥${value.toFixed(2)}`;
}

function sortLabel(value: string) {
  switch (value) {
    case "lowest_price":
      return "价格最低";
    case "highest_profit":
      return "利润最高";
    case "highest_score":
      return "评分最高";
    case "lowest_risk":
      return "风险最低";
    default:
      return "最新";
  }
}
