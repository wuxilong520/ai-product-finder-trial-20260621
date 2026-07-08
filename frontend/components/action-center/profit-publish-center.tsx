"use client";

import { useMemo, useState } from "react";
import { Loader2, ShieldCheck, UploadCloud, WandSparkles } from "lucide-react";

import { Badge, Button, Card, CardContent, CardHeader, CardTitle, EmptyState, InfoTile, Input, StatusAlert, StatusBadge } from "@/design-system/components";
import { runDecisionV1, runListingV1, runPublishV1 } from "@/lib/api-gateway";
import { getToken } from "@/lib/auth";
import type { DecisionV1Response, ListingV1Response, PublishV1Response } from "@/lib/types";

type MarketValue = "shopify" | "amazon" | "shopee" | "tiktok";
type StrategyMode = "sourcing" | "listing" | "scaling";

const DEFAULT_KEYWORD = "air fryer";

export function ProfitPublishCenter({ initialKeyword }: { initialKeyword?: string }) {
  const [keyword, setKeyword] = useState(initialKeyword || DEFAULT_KEYWORD);
  const [market, setMarket] = useState<MarketValue>("shopify");
  const [strategyMode, setStrategyMode] = useState<StrategyMode>("listing");
  const [productCost, setProductCost] = useState("39");
  const [shippingCost, setShippingCost] = useState("12");
  const [adCost, setAdCost] = useState("8");
  const [platformFee, setPlatformFee] = useState("6");
  const [shopDomain, setShopDomain] = useState("");

  const [decisionData, setDecisionData] = useState<DecisionV1Response | null>(null);
  const [listingData, setListingData] = useState<ListingV1Response | null>(null);
  const [publishData, setPublishData] = useState<PublishV1Response | null>(null);

  const [decisionLoading, setDecisionLoading] = useState(false);
  const [listingLoading, setListingLoading] = useState(false);
  const [publishLoading, setPublishLoading] = useState(false);
  const [error, setError] = useState("");

  const constraints = useMemo(
    () => ({
      product_cost: Number(productCost || 0),
      shipping_cost: Number(shippingCost || 0),
      ad_cost: Number(adCost || 0),
      platform_fee: Number(platformFee || 0),
    }),
    [adCost, platformFee, productCost, shippingCost]
  );

  async function handleRunDecision() {
    const finalKeyword = keyword.trim();
    if (!finalKeyword) {
      setError("请先输入你要做的商品关键词。");
      return;
    }
    setDecisionLoading(true);
    setListingData(null);
    setPublishData(null);
    setError("");
    try {
      const result = await runDecisionV1(
        {
          keyword: finalKeyword,
          market,
          strategy_mode: strategyMode,
          business_constraints: constraints,
        },
        getToken()
      );
      setDecisionData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "利润决策失败");
      setDecisionData(null);
    } finally {
      setDecisionLoading(false);
    }
  }

  async function handleBuildListing() {
    const finalKeyword = keyword.trim();
    if (!finalKeyword) {
      setError("请先输入你要做的商品关键词。");
      return;
    }
    setListingLoading(true);
    setPublishData(null);
    setError("");
    try {
      const result = await runListingV1(
        {
          keyword: finalKeyword,
          market,
          channel: "shopify",
        },
        getToken()
      );
      setListingData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "上架草稿生成失败");
      setListingData(null);
    } finally {
      setListingLoading(false);
    }
  }

  async function handlePublishCheck() {
    const finalKeyword = keyword.trim();
    if (!finalKeyword) {
      setError("请先输入你要做的商品关键词。");
      return;
    }
    if (!shopDomain.trim()) {
      setError("请先填 Shopify 店铺域名，再做发布检查。");
      return;
    }
    setPublishLoading(true);
    setError("");
    try {
      const result = await runPublishV1(
        {
          keyword: finalKeyword,
          market,
          channel: "shopify",
          shop_domain: shopDomain.trim(),
        },
        getToken()
      );
      setPublishData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "发布检查失败");
      setPublishData(null);
    } finally {
      setPublishLoading(false);
    }
  }

  const decision = decisionData?.decision;
  const analysis = decisionData?.analysis;
  const explain = decisionData?.explain;
  const listing = listingData?.listing;
  const bootstrap = listingData?.production_bootstrap_status;

  return (
    <div className="space-y-5">
      <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
        <CardHeader>
          <div className="text-xs uppercase tracking-[0.24em] text-white/40">商航AI · 利润决策 + 上架准备页</div>
          <CardTitle>先确认这单到底赚不赚钱，再决定要不要继续推进上架</CardTitle>
          <p className="text-sm text-white/55">
            这一步不是一上来就发布，而是先把利润、风险、执行等级和发布条件看清楚，再决定要不要继续做 Shopify 上架准备。
          </p>
        </CardHeader>
        <CardContent className="space-y-4">
          {error ? <StatusAlert status="error" message={error} /> : null}
          <StatusAlert
            status="warning"
            title="当前真实边界"
            message="现在这页已经接上真实决策、上架草稿和发布前检查接口。但真实发布仍然受 production_ready 锁控制，锁没开时不会假装说已经可商用自动发布。"
          />
          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
            <InfoTile label="当前商品" value={keyword || "未填写"} />
            <InfoTile label="当前市场" value={market} />
            <InfoTile label="当前策略" value={strategyMode} />
            <InfoTile label="当前目标" value="做最后拍板" />
          </div>
          <div className="grid gap-4 md:grid-cols-4">
            <StepHint title="先看利润" desc="如果利润不成立，后面就没有必要继续做上架准备。" />
            <StepHint title="再看风险" desc="利润看起来不错，也要判断风险和执行等级。" />
            <StepHint title="再生成草稿" desc="确认值得继续后，再生成 Shopify 上架草稿。" />
            <StepHint title="最后做检查" desc="检查当前到底允不允许往真实发布走。" />
          </div>
          <div className="grid gap-3 md:grid-cols-2">
            <Input value={keyword} onChange={(event) => setKeyword(event.target.value)} placeholder="例如：air fryer" />
            <Input value={shopDomain} onChange={(event) => setShopDomain(event.target.value)} placeholder="Shopify 店铺域名，例如 your-store.myshopify.com" />
          </div>
          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
            <label className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white">
              <div className="mb-2 text-white/55">市场</div>
              <select value={market} onChange={(event) => setMarket(event.target.value as MarketValue)} className="w-full bg-transparent outline-none">
                <option value="shopify" className="bg-[#111827]">shopify</option>
                <option value="amazon" className="bg-[#111827]">amazon</option>
                <option value="shopee" className="bg-[#111827]">shopee</option>
                <option value="tiktok" className="bg-[#111827]">tiktok</option>
              </select>
            </label>
            <label className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white">
              <div className="mb-2 text-white/55">策略模式</div>
              <select value={strategyMode} onChange={(event) => setStrategyMode(event.target.value as StrategyMode)} className="w-full bg-transparent outline-none">
                <option value="sourcing" className="bg-[#111827]">sourcing</option>
                <option value="listing" className="bg-[#111827]">listing</option>
                <option value="scaling" className="bg-[#111827]">scaling</option>
              </select>
            </label>
            <Input value={productCost} onChange={(event) => setProductCost(event.target.value)} placeholder="商品成本" />
            <Input value={shippingCost} onChange={(event) => setShippingCost(event.target.value)} placeholder="运费成本" />
            <Input value={adCost} onChange={(event) => setAdCost(event.target.value)} placeholder="广告成本" />
            <Input value={platformFee} onChange={(event) => setPlatformFee(event.target.value)} placeholder="平台抽佣" />
          </div>
          <div className="flex flex-wrap gap-3">
            <Button type="button" onClick={() => void handleRunDecision()} disabled={decisionLoading}>
              {decisionLoading ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />正在计算利润决策</> : <>先做利润决策</>}
            </Button>
            <Button type="button" variant="secondary" onClick={() => void handleBuildListing()} disabled={listingLoading}>
              {listingLoading ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />正在生成草稿</> : <>生成 Shopify 上架草稿</>}
            </Button>
            <Button type="button" variant="ghost" onClick={() => void handlePublishCheck()} disabled={publishLoading}>
              {publishLoading ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />正在检查发布</> : <>做发布前检查</>}
            </Button>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-5 xl:grid-cols-[1.05fr_0.95fr]">
        <div className="space-y-5">
          <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <WandSparkles className="h-5 w-5 text-[#7dd3fc]" />
                最后拍板结果
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {decision ? (
                <>
                  <div className="flex flex-wrap gap-3">
                    <Badge variant="brand">决策分 {roundScore(decision.decision_score)}</Badge>
                    <StatusBadge status={decision.risk_level === "low" ? "success" : decision.risk_level === "medium" ? "warning" : "blocked"} label={`风险 ${decision.risk_level || "unknown"}`} />
                    <StatusBadge status={decision.execution_allowed ? "success" : "blocked"} label={decision.action_level || "未给出执行等级"} />
                  </div>
                  <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                    <InfoTile label="真实利润估算" value={formatMoney(decision.real_profit_estimate)} />
                    <InfoTile label="信任调整后分数" value={roundScore(decision.trust_adjusted_score)} />
                    <InfoTile label="上架建议" value={decision.listing_recommendation || "—"} />
                    <InfoTile label="执行是否允许" value={decision.execution_allowed ? "允许" : "不允许"} />
                    <InfoTile label="执行阻断原因" value={decision.execution_block_reason || "当前没有阻断"} />
                    <InfoTile label="策略模式" value={decision.strategy_mode || "—"} />
                  </div>
                  <div className="rounded-2xl border border-white/8 bg-black/10 p-4 text-sm leading-7 text-white/68">
                    {buildDecisionSummary(decision)}
                  </div>
                  <div className="grid gap-4 md:grid-cols-2">
                    <InfoTile label="市场摘要" value={analysis?.market_insight?.summary || "后端没返回市场摘要"} />
                    <InfoTile label="可信数据状态" value={formatTrustLine(analysis?.trust_report)} />
                  </div>
                  <div className="rounded-2xl border border-white/8 bg-white/[0.03] p-4">
                    <div className="text-sm font-medium text-white">AI 给出的下一步</div>
                    <div className="mt-3 space-y-2 text-sm leading-7 text-white/65">
                      {(explain?.next_actions?.length ? explain.next_actions : decision.execution_steps || []).map((item) => (
                        <div key={item}>- {item}</div>
                      ))}
                    </div>
                  </div>
                  <div className="rounded-2xl border border-white/8 bg-white/[0.03] p-4">
                    <div className="text-sm font-medium text-white">AI 解释</div>
                    <div className="mt-3 text-sm leading-7 text-white/65">{explain?.summary || "当前没有额外解释摘要"}</div>
                  </div>
                </>
              ) : (
                <EmptyState text="你先点“先做利润决策”，这里才会出现真实结果。" />
              )}
            </CardContent>
          </Card>

          <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <UploadCloud className="h-5 w-5 text-[#60a5fa]" />
                Shopify 上架草稿
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {listing ? (
                <>
                  <div className="grid gap-4 md:grid-cols-2">
                    <InfoTile label="草稿标题" value={listing.listing_title || listing.product_title || "—"} />
                    <InfoTile label="SEO 标题" value={listing.seo_title || "—"} />
                    <InfoTile label="建议售价" value={formatMoney(listing.suggested_price ?? listing.price_suggestion)} />
                    <InfoTile label="发布建议" value={listingData?.publish_decision || "—"} />
                    <InfoTile label="执行目标平台" value={listingData?.execution_target_platform || "—"} />
                    <InfoTile label="执行状态" value={listingData?.execution?.platform_execution_status || "—"} />
                  </div>
                  <div className="rounded-2xl border border-white/8 bg-black/10 p-4 text-sm leading-7 text-white/68">
                    这一步的作用不是直接发布，而是先把 Shopify 的商品草稿准备出来，方便你继续检查标题、售价、卖点和关键词。
                  </div>
                  <div className="rounded-2xl border border-white/8 bg-white/[0.03] p-4">
                    <div className="text-sm font-medium text-white">卖点</div>
                    <div className="mt-3 space-y-2 text-sm leading-7 text-white/65">
                      {(listing.selling_points || listing.bullet_points || []).map((item) => (
                        <div key={item}>- {item}</div>
                      ))}
                    </div>
                  </div>
                  <div className="rounded-2xl border border-white/8 bg-white/[0.03] p-4">
                    <div className="text-sm font-medium text-white">关键词</div>
                    <div className="mt-3 flex flex-wrap gap-2">
                      {(listing.keywords || []).length ? (
                        (listing.keywords || []).map((item) => (
                          <Badge key={item} variant="neutral">{item}</Badge>
                        ))
                      ) : (
                        <div className="text-sm text-white/55">当前没有关键词列表</div>
                      )}
                    </div>
                  </div>
                </>
              ) : (
                <EmptyState text="你先点“生成 Shopify 上架草稿”，这里才会出现真实草稿。" />
              )}
            </CardContent>
          </Card>
        </div>

        <div className="space-y-5">
          <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ShieldCheck className="h-5 w-5 text-[#34d399]" />
                发布前检查
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {publishData ? (
                <>
                  <div className="flex flex-wrap gap-3">
                    <StatusBadge
                      status={publishData.execution_bridge_mapping?.publish_allowed ? "success" : "blocked"}
                      label={publishData.platform_execution_status || "未返回平台执行状态"}
                    />
                    <Badge variant={publishData.product_mode === "production_mode" ? "success" : "warning"}>
                      {publishData.product_mode || "未知模式"}
                    </Badge>
                  </div>
                  <div className="grid gap-4 md:grid-cols-2">
                    <InfoTile label="执行队列状态" value={publishData.execution_queue_status || "—"} />
                    <InfoTile label="平台动作" value={String(publishData.execution_bridge_mapping?.platform_action || "—")} />
                    <InfoTile label="是否允许发布" value={publishData.execution_bridge_mapping?.publish_allowed ? "允许" : "不允许"} />
                    <InfoTile label="Shopify 商品 ID" value={publishData.shopify_product_id || "还没有"} />
                  </div>
                  <div className="rounded-2xl border border-white/8 bg-black/10 p-4 text-sm leading-7 text-white/68">
                    {publishData.execution_bridge_mapping?.publish_allowed
                      ? "从当前检查结果看，这一步已经接近可以往真实发布推进。"
                      : "从当前检查结果看，这一步还不能直接往真实发布走，先解决阻塞项。"}
                  </div>
                  <div className="rounded-2xl border border-white/8 bg-white/[0.03] p-4">
                    <div className="text-sm font-medium text-white">检查结论</div>
                    <div className="mt-3 text-sm leading-7 text-white/65">{publishData.message || "当前没有额外说明"}</div>
                  </div>
                  <div className="rounded-2xl border border-white/8 bg-white/[0.03] p-4">
                    <div className="text-sm font-medium text-white">阻塞项</div>
                    <div className="mt-3 space-y-2 text-sm leading-7 text-white/65">
                      {(publishData.blocking_items?.length ? publishData.blocking_items : ["当前没有额外阻塞项"]).map((item) => (
                        <div key={item}>- {item}</div>
                      ))}
                    </div>
                  </div>
                </>
              ) : (
                <EmptyState text="你先点“做发布前检查”，这里才会告诉你现在能不能往 Shopify 走。" />
              )}
            </CardContent>
          </Card>

          <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <CardTitle>这一页当前能帮你做到哪里</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm leading-7 text-white/60">
              <div>1. 已经能做：利润估算、风险判断、执行等级判断、Shopify 上架草稿生成、发布前检查。</div>
              <div>2. 还不能乱说：已经真实自动发布成功。因为真实发布仍会被 production_ready 生产锁控制。</div>
              <div>3. 现在最真实的闭环是：市场页 → 商品机会页 → 供应链匹配页 → 这一页做最后拍板和上架准备。</div>
            </CardContent>
          </Card>

          <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <CardTitle>生产锁状态</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <InfoTile label="product_mode" value={bootstrap?.product_mode || publishData?.product_mode || "当前还没拿到"} />
              <InfoTile label="production_ready" value={bootstrap?.production_ready === undefined ? "当前还没拿到" : bootstrap.production_ready ? "true" : "false"} />
              <div className="rounded-2xl border border-white/8 bg-white/[0.03] p-4 text-sm leading-7 text-white/65">
                {(bootstrap?.blocking_items?.length ? bootstrap.blocking_items : publishData?.blocking_items || ["当前还没返回生产阻塞项"]).map((item) => (
                  <div key={item}>- {item}</div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

function formatMoney(value?: number | null) {
  if (value === undefined || value === null || Number.isNaN(Number(value))) {
    return "—";
  }
  return `¥${Number(value).toFixed(2)}`;
}

function roundScore(value?: number | null) {
  if (value === undefined || value === null || Number.isNaN(Number(value))) {
    return "—";
  }
  return `${Math.round(Number(value))} / 100`;
}

function formatTrustLine(
  trust?: {
    trust_level?: number;
    confidence?: number;
    is_mock?: boolean;
    is_expired?: boolean;
    data_trust_score?: number;
  }
) {
  if (!trust) {
    return "后端还没返回可信数据说明";
  }
  return `trust=${trust.trust_level ?? "—"} / confidence=${trust.confidence ?? "—"} / mock=${String(trust.is_mock ?? false)} / expired=${String(trust.is_expired ?? false)}`;
}

function StepHint({ title, desc }: { title: string; desc: string }) {
  return (
    <div className="rounded-2xl border border-white/8 bg-white/5 p-4">
      <div className="text-base font-semibold text-white">{title}</div>
      <div className="mt-2 text-sm leading-7 text-white/60">{desc}</div>
    </div>
  );
}

function buildDecisionSummary(decision: NonNullable<DecisionV1Response["decision"]>) {
  const profitOk = typeof decision.real_profit_estimate === "number" && decision.real_profit_estimate > 0;
  const riskText = decision.risk_level === "low" ? "风险偏低" : decision.risk_level === "medium" ? "风险中等" : "风险偏高";
  const actionText = decision.action_level || "还没给出执行等级";

  if (profitOk && decision.execution_allowed) {
    return `这轮结果说明：利润目前看起来能成立，${riskText}，而且执行等级是 ${actionText}，可以继续推进 Shopify 上架准备。`;
  }
  if (profitOk) {
    return `这轮结果说明：利润目前不算差，但 ${riskText}，或者执行条件还没满足，所以现在更适合先解决阻塞项。`;
  }
  return `这轮结果说明：利润现在还不够成立，同时 ${riskText}，这时不适合急着推进上架。`;
}
