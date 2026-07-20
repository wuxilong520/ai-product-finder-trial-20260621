"use client";

import { useEffect, useMemo, useState } from "react";
import { ExternalLink, Loader2, Search } from "lucide-react";

import { Badge, Button, Card, CardContent, CardHeader, CardTitle, EmptyState, Input, InfoTile, KpiTile, SectionIntro, StatusBadge, Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/design-system/components";
import { ROUTES } from "@/config/routes";
import { createSupplyExtensionCode, matchSuppliers } from "@/lib/api-gateway";
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
  const [sortBy, setSortBy] = useState<"highest_score" | "lowest_price" | "lowest_risk">("highest_score");
  const [extensionCode, setExtensionCode] = useState("");
  const [extensionCodeCopied, setExtensionCodeCopied] = useState(false);
  const [extensionLoading, setExtensionLoading] = useState(false);
  const [extensionError, setExtensionError] = useState("");

  async function handleCreateExtensionCode() {
    const token = getToken();
    if (!token) {
      window.location.href = ROUTES.login;
      return;
    }
    setExtensionLoading(true);
    setExtensionError("");
    setExtensionCodeCopied(false);
    try {
      const result = await createSupplyExtensionCode(token);
      setExtensionCode(result.extension_code);
    } catch (err) {
      setExtensionError(err instanceof Error ? err.message : "生成连接码失败");
      setExtensionCode("");
    } finally {
      setExtensionLoading(false);
    }
  }

  async function handleCopyExtensionCode() {
    if (!extensionCode) return;
    await navigator.clipboard.writeText(extensionCode);
    setExtensionCodeCopied(true);
  }

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
    const baseFiltered = items.filter((item) => {
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
    if (availableOnly && baseFiltered.length === 0 && items.length > 0) {
      return items.filter((item) => {
        if (!Number.isNaN(scoreFloor) && item.match_score < scoreFloor) {
          return false;
        }
        if (priceLimit !== null && !Number.isNaN(priceLimit) && item.supplier_price != null && item.supplier_price > priceLimit) {
          return false;
        }
        return true;
      });
    }
    return baseFiltered;
  }, [availableOnly, items, maxPrice, minScore]);

  const rankedItems = useMemo(() => {
    const list = [...filteredItems];
    if (sortBy === "lowest_price") {
      return list.sort((a, b) => (a.supplier_price ?? Number.MAX_SAFE_INTEGER) - (b.supplier_price ?? Number.MAX_SAFE_INTEGER));
    }
    if (sortBy === "lowest_risk") {
      return list.sort((a, b) => riskWeight(a.risk_level) - riskWeight(b.risk_level));
    }
    return list.sort((a, b) => {
      const scoreA = Number(a.supplier_real_score ?? a.supplier_score ?? a.match_score ?? 0);
      const scoreB = Number(b.supplier_real_score ?? b.supplier_score ?? b.match_score ?? 0);
      return scoreB - scoreA;
    });
  }, [filteredItems, sortBy]);

  return (
    <div className="space-y-5">
      <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
        <CardContent className="p-6">
          <SectionIntro
            eyebrow="商航AI · 供应链竞争中心"
            title="把供应商当成竞争池来比较，而不是后台列表"
            description="这一步不是拍板上架，而是先确认：这个商品有没有价格合适、供应更稳、MOQ 更合理、风险更低的供应商。你可以先排序，再决定要不要继续采购。"
          />
        </CardContent>
      </Card>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <KpiTile label="当前商品" value={keyword || "未指定"} hint="现在正在比较的商品关键词" />
        <KpiTile label="供应商数量" value={`${rankedItems.length} 个`} hint="当前筛选后还能继续看的供应商数量" />
        <KpiTile label="当前筛选" value={availableOnly ? "只看可供货" : "显示全部"} hint="避免把没货的结果排到前面" />
        <KpiTile label="当前排序" value={sortByLabel(sortBy)} hint="你可以自己决定按评分、价格或风险看" />
      </div>

      <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
        <CardContent className="space-y-4">
          <div className="grid gap-3 md:grid-cols-3">
            <InfoTile label="当前类目" value={initialCategory || "未指定"} />
            <InfoTile label="当前商品" value={keyword || "未指定"} />
            <InfoTile label="当前阶段" value="筛货源" />
          </div>
          <div className="grid gap-3 md:grid-cols-3">
            <InfoTile label="当前结果数" value={`${filteredItems.length} 个`} />
            <InfoTile
              label="当前最低匹配分"
              value={`${Number.isNaN(Number(minScore || 0)) ? 0 : Number(minScore || 0)} 分`}
            />
            <InfoTile
              label="当前筛选重点"
              value={availableOnly ? "只看可供货" : "全部供应结果"}
            />
          </div>
          <div className="grid gap-4 md:grid-cols-4">
            <StepCard title="先比价格" desc="先过滤掉明显超出你成本预期的货源。" />
            <StepCard title="再看匹配分" desc="优先看和当前商品方向更接近的货源。" />
            <StepCard title="再看是否有货" desc="没有现货或无法供货的，先别浪费时间。" />
            <StepCard title="最后进利润页" desc="筛完货源后，再去做最后的利润判断。" />
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
          <div className="grid gap-3 md:grid-cols-3">
            {[
              ["highest_score", "评分最高"],
              ["lowest_price", "价格最低"],
              ["lowest_risk", "风险最低"],
            ].map(([value, label]) => (
              <button
                key={value}
                type="button"
                onClick={() => setSortBy(value as "highest_score" | "lowest_price" | "lowest_risk")}
                className={`rounded-2xl border px-4 py-3 text-sm transition ${sortBy === value ? "border-[#4F7CFF]/30 bg-[#4F7CFF]/12 text-[#D8E3FF]" : "border-white/10 bg-white/5 text-white/70 hover:bg-white/10"}`}
              >
                {label}
              </button>
            ))}
          </div>
          <div className="rounded-2xl border border-[#4F7CFF]/20 bg-[#4F7CFF]/10 px-4 py-3 text-sm leading-7 text-[#D8E3FF]">
            当前这页已经能真实展示：供应商推荐、价格、MOQ、供应稳定性、可信度、认证情况、利润预估、风险提示。还没完全打通的是真实 1688 官方接口，不会假装成已接通。
          </div>
          <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
            <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
              <div>
                <div className="text-sm font-semibold text-white">安装1688供应链助手</div>
                <div className="mt-1 text-sm leading-7 text-white/60">
                  通过浏览器插件同步你自己在 1688 页面里主动查看到的公开供应商数据。不会读取账号密码，也不会上传 Cookie。
                </div>
              </div>
              <div className="flex flex-wrap gap-2">
                <Button type="button" variant="secondary" onClick={() => window.alert("插件源码目录：frontend/extensions/1688-supply-assistant\n请按报告里的步骤，用 Chrome 加载已解压的扩展程序。")}>
                  安装1688供应链助手
                </Button>
                <Button type="button" onClick={() => void handleCreateExtensionCode()} disabled={extensionLoading}>
                  {extensionLoading ? "生成中..." : "生成连接码"}
                </Button>
              </div>
            </div>
            <div className="mt-3 rounded-2xl border border-white/8 bg-black/10 px-4 py-3 text-sm text-white/75">
              真实流程：登录商航AI → 生成连接码 → 在插件里输入连接码 → 打开1688商品页 → 点击“同步当前商品”。
            </div>
            {extensionError ? (
              <div className="mt-3 rounded-2xl border border-rose-400/20 bg-rose-400/10 px-4 py-3 text-sm text-rose-200">
                {extensionError}
              </div>
            ) : null}
            {extensionCode ? (
              <div className="mt-3 rounded-2xl border border-emerald-400/20 bg-emerald-400/10 px-4 py-3 text-sm text-emerald-100">
                <div>当前连接码：<span className="font-semibold tracking-[0.18em]">{extensionCode}</span></div>
                <div className="mt-1 text-emerald-100/80">10分钟内有效，只能用于把插件连到你自己的商航AI账号。</div>
                <div className="mt-3 flex flex-wrap gap-2">
                  <Button type="button" variant="secondary" onClick={() => void handleCopyExtensionCode()}>
                    {extensionCodeCopied ? "已复制连接码" : "复制连接码"}
                  </Button>
                </div>
              </div>
            ) : null}
          </div>
          {availableOnly && items.length > 0 && filteredItems.length > 0 && filteredItems.length === items.filter((item) => {
            const priceLimit = maxPrice ? Number(maxPrice) : null;
            const scoreFloor = Number(minScore || 0);
            if (!Number.isNaN(scoreFloor) && item.match_score < scoreFloor) {
              return false;
            }
            if (priceLimit !== null && !Number.isNaN(priceLimit) && item.supplier_price != null && item.supplier_price > priceLimit) {
              return false;
            }
            return true;
          }).length && !items.some((item) => /available|instock|ready|现货|有货/i.test(item.availability || "")) ? (
            <div className="rounded-2xl border border-amber-400/20 bg-amber-400/10 px-4 py-3 text-sm text-amber-100">
              当前没有“可供货”状态的实时结果，这里先把待核验供应结果展示给你，避免页面空白。
            </div>
          ) : null}
          <div className="grid gap-4 md:grid-cols-3">
            <HintCard
              title="先筛价格"
              desc="先把你能接受的供货价格卡住，避免后面利润算半天，最后发现进货价根本不合适。"
            />
            <HintCard
              title="再看匹配分"
              desc="匹配分越高，说明它和你当前关键词、商品方向越接近，优先看前面的。"
            />
            <HintCard
              title="最后进利润页"
              desc="这里只是找货和比价，不是最终拍板。筛完供应链，再去利润决策页做最后判断。"
            />
          </div>
          {error ? <div className="rounded-2xl border border-rose-400/20 bg-rose-400/10 px-4 py-3 text-sm text-rose-200">{error}</div> : null}
        </CardContent>
      </Card>

      <div className="grid gap-5 xl:grid-cols-[1.1fr_0.9fr]">
        <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <CardHeader>
            <CardTitle>供应商排行卡</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {rankedItems.length ? rankedItems.map((item, index) => (
              <a key={`${item.platform}-${item.supplier_url}-${index}`} href={item.supplier_url} target="_blank" rel="noreferrer" className="block rounded-[18px] border border-white/8 bg-white/[0.03] p-4 transition hover:bg-white/[0.06]">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge variant="neutral">#{index + 1}</Badge>
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
                <div className="mt-4 rounded-2xl border border-white/8 bg-black/10 p-4 text-sm leading-7 text-white/68">
                  {buildSupplierSummary(item)}
                </div>
                <div className="mt-4 grid gap-4 md:grid-cols-4">
                  <InfoTile label={text.supplierPrice} value={item.supplier_price != null ? `${item.currency || ""} ${Number(item.supplier_price).toFixed(2)}` : text.supplierPending} />
                  <InfoTile label="MOQ" value={item.moq != null ? `${item.moq}` : "待确认"} />
                  <InfoTile label="供应稳定性" value={item.supplier_score != null ? `${Number(item.supplier_score).toFixed(1)} / ${item.supplier_level || "—"}` : "待判断"} />
                  <InfoTile label={text.supplierStatus} value={item.availability} />
                </div>
                <div className="mt-4 grid gap-4 md:grid-cols-4">
                  <InfoTile label="供应商真实性" value={item.supplier_real_score != null ? `${Number(item.supplier_real_score).toFixed(1)} / 100` : "待判断"} />
                  <InfoTile label="价格竞争力" value={item.price_competitiveness_score != null ? `${Number(item.price_competitiveness_score).toFixed(1)}` : "待判断"} />
                  <InfoTile label="供应风险" value={item.risk_level || "待判断"} />
                  <InfoTile label="采购建议" value={item.procurement_recommendation || "待判断"} />
                </div>
                <div className="mt-4 grid gap-4 md:grid-cols-4">
                  <InfoTile label="供应可信度" value={item.supplier_confidence != null ? `${Math.round(Number(item.supplier_confidence) * 100)}%` : "待确认"} />
                  <InfoTile label="认证情况" value={item.certification || "暂无"} />
                  <InfoTile label="交付时效" value={item.delivery_time ? `${item.delivery_time} 天` : "待确认"} />
                  <InfoTile label="MOQ合理性" value={item.moq_score != null ? `${Number(item.moq_score).toFixed(1)}` : "待判断"} />
                </div>
                {(item.risk_flags || []).length ? (
                  <div className="mt-4 flex flex-wrap gap-2">
                    {(item.risk_flags || []).slice(0, 4).map((flag) => (
                      <Badge key={flag} variant="warning">{flag}</Badge>
                    ))}
                  </div>
                ) : null}
                <div className="mt-4 flex flex-wrap gap-3">
                  <Link
                    href={`${ROUTES.actionProfit}${keyword ? `?keyword=${encodeURIComponent(keyword)}` : ""}`}
                    className="rounded-2xl border border-[#4F7CFF]/20 bg-[#4F7CFF]/10 px-4 py-2 text-sm font-medium text-[#D8E3FF] transition hover:bg-[#4F7CFF]/16"
                  >
                    用这个结果继续做利润决策
                  </Link>
                  <Link
                    href={item.supplier_url}
                    target="_blank"
                    className="rounded-2xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-white/80 transition hover:bg-white/10"
                  >
                    查看供应商详情
                  </Link>
                  <Link
                    href={`${ROUTES.createTask}?keyword=${encodeURIComponent(keyword || item.supplier_title)}`}
                    className="rounded-2xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-white/80 transition hover:bg-white/10"
                  >
                    重新跑这个商品
                  </Link>
                </div>
              </a>
            )) : <EmptyState title={items.length ? "当前筛选下没有供应商" : "当前还没有供应商结果"} text={items.length ? "你可以放宽价格、评分或可供货筛选条件。" : text.supplierEmpty} />}
          </CardContent>
        </Card>

        <div className="space-y-5">
          <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <CardTitle>这一步到底在决定什么</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-4 md:grid-cols-3">
              <HintCard title="能不能拿货" desc="如果没货，后面利润和上架都没有意义。" />
              <HintCard title="价格能不能承接" desc="如果供货价太高，利润页基本很难跑出好结果。" />
              <HintCard title="要不要继续推进" desc="这里只筛采购可行性，最后拍板还是要去利润决策页。" />
            </CardContent>
          </Card>

          <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <CardTitle>报价对比</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <tr>
                    <TableHead>排行</TableHead>
                    <TableHead>供应商</TableHead>
                    <TableHead>{text.supplierPlatform}</TableHead>
                    <TableHead>{text.supplierPrice}</TableHead>
                    <TableHead>真实性评分</TableHead>
                    <TableHead>价格竞争力</TableHead>
                    <TableHead>风险</TableHead>
                  </tr>
                </TableHeader>
                <TableBody>
                  {rankedItems.map((item, index) => (
                    <TableRow key={`table-${item.platform}-${index}`}>
                      <TableCell>#{index + 1}</TableCell>
                      <TableCell>{item.supplier_name || item.supplier_title}</TableCell>
                      <TableCell>{item.platform}</TableCell>
                      <TableCell>{item.supplier_price != null ? `${item.currency || ""} ${Number(item.supplier_price).toFixed(2)}` : text.supplierPending}</TableCell>
                      <TableCell>{item.supplier_real_score != null ? Number(item.supplier_real_score).toFixed(1) : "待判断"}</TableCell>
                      <TableCell>{item.price_competitiveness_score != null ? Number(item.price_competitiveness_score).toFixed(1) : "待判断"}</TableCell>
                      <TableCell>{item.risk_level || "待判断"}</TableCell>
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
              {rankedItems.slice(0, 5).map((item, index) => (
                <div key={`rank-${item.platform}-${index}`} className="flex items-center justify-between rounded-[16px] border border-white/8 bg-white/[0.03] px-4 py-3">
                  <div>
                    <div className="text-sm font-medium text-white">TOP {index + 1} · {item.platform}</div>
                    <div className="mt-1 text-xs text-white/45">{item.supplier_title}</div>
                  </div>
                  <Badge variant={riskWeight(item.risk_level) === 1 ? "success" : riskWeight(item.risk_level) === 2 ? "warning" : "error"} className="px-3 py-1.5 text-sm">
                    {item.procurement_recommendation || Math.round(item.match_score)}
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

          <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <CardTitle>这一页现在的真实边界</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm leading-7 text-white/60">
              <div>1. 现在已经能做：关键词匹配、1688 供货结果查看、价格筛选、匹配分筛选、是否有货筛选。</div>
              <div>2. 现在已经能展示：真实性、MOQ、认证、风险、采购建议；但 1688 官方实时明细还没完全接通。</div>
              <div>3. 你现在最适合的真实流程是：市场页 → 商品机会页 → 供应链匹配页 → 利润决策页。</div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

function sortByLabel(value: "highest_score" | "lowest_price" | "lowest_risk") {
  if (value === "lowest_price") return "价格最低";
  if (value === "lowest_risk") return "风险最低";
  return "评分最高";
}

function riskWeight(value?: string | null) {
  const normalized = String(value || "").toLowerCase();
  if (normalized === "low") return 1;
  if (normalized === "medium") return 2;
  if (normalized === "high") return 3;
  return 9;
}

function HintCard({ title, desc }: { title: string; desc: string }) {
  return (
    <div className="rounded-2xl border border-white/8 bg-white/5 p-4">
      <div className="text-base font-semibold text-white">{title}</div>
      <div className="mt-2 text-sm leading-7 text-white/60">{desc}</div>
    </div>
  );
}

function StepCard({ title, desc }: { title: string; desc: string }) {
  return (
    <div className="rounded-2xl border border-white/8 bg-white/5 p-4">
      <div className="text-base font-semibold text-white">{title}</div>
      <div className="mt-2 text-sm leading-7 text-white/60">{desc}</div>
    </div>
  );
}

function buildSupplierSummary(item: SupplierMatchItem) {
  const priceText = item.supplier_price != null ? "价格已经返回" : "价格还没完整返回";
  const scoreText = item.match_score >= 70 ? "匹配度比较高" : item.match_score >= 45 ? "匹配度中等" : "匹配度偏弱";
  const stockText = /available|instock|ready|现货|有货/i.test(item.availability || "") ? "当前看起来还能供货" : "当前供货状态一般";
  const supplierText = item.supplier_real_score != null
    ? `真实性大约 ${Number(item.supplier_real_score).toFixed(1)} 分`
    : item.supplier_score != null
      ? `供应稳定性大约 ${Number(item.supplier_score).toFixed(1)} 分`
      : "供应稳定性还在补充";
  const riskText = (item.risk_flags || []).length ? `需要留意 ${(item.risk_flags || []).slice(0, 2).join("、")}` : "当前没有额外风险提示";
  return `${item.platform} 这条货源现在 ${scoreText}，${stockText}，${priceText}，${supplierText}，${riskText}。`;
}
