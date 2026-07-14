import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { ShopifyConnectCard } from "@/components/market/shopify-connect-card";
import { ROUTES } from "@/config/routes";
import { Badge, Button, Card, CardContent, KpiTile, SectionIntro } from "@/design-system/components";
import { analyzeOpportunity, getOpportunityHistory } from "@/lib/api";
import { getMarketConnections } from "@/lib/api/market";

export default async function OpportunityDashboardPage() {
  const cookieStore = await cookies();
  const token = cookieStore.get("shanghang_token")?.value;
  const lang = (cookieStore.get("shanghang_lang")?.value as "zh" | "en") || "zh";
  if (!token) redirect(ROUTES.login);

  const keyword = "wireless earbuds";
  const [opportunity, history, connections] = await Promise.all([
    analyzeOpportunity({ keyword, marketplace: "US", region: "US" }, token),
    getOpportunityHistory(token, 12),
    getMarketConnections(token).catch(() => ({})),
  ]);

  const opportunitySummary = buildOpportunitySummary(opportunity.decision);
  const latestHistory = history.items[0];

  return (
    <XBorderLayout lang={lang} activePath="action">
      <div className="space-y-6">
        <Card className="border-white/8 bg-[#111A2E]">
          <CardContent className="p-6">
            <SectionIntro
              eyebrow="商航AI · 商业机会中心"
              title="把市场、供应链、利润和执行放在一条线上看"
              description="这页只回答一件事：这个商品方向值不值得推进。你看完就能决定是观察、测试还是继续放量。"
            />
          </CardContent>
        </Card>

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
          <KpiTile label="市场评分" value={String(opportunity.market_score)} hint={`需求 ${opportunity.market_signal.demand_score} / 趋势 ${opportunity.market_signal.trend_direction}`} />
          <KpiTile label="利润空间" value={`${opportunity.profit_margin.toFixed(2)}%`} hint={`预估售价 ${opportunity.profit_signal.expected_price}`} />
          <KpiTile label="供应难度" value={String(opportunity.supplier_score)} hint={`来源 ${opportunity.supplier_signal.supplier_source}`} />
          <KpiTile label="机会总分" value={String(opportunity.opportunity_score)} hint={`可信度 ${(opportunity.confidence * 100).toFixed(0)}%`} />
          <KpiTile label="当前动作" value={opportunity.decision} hint={opportunitySummary} className={decisionToneClass(opportunity.decision)} />
        </div>

        <ShopifyConnectCard token={token} initialConnection={(connections as Record<string, any>)?.shopify} />

        <div className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
          <Card className="border-white/8 bg-[#111A2E] p-6">
            <div className="flex items-start justify-between gap-4">
              <div>
                <div className="text-sm font-medium text-white">这次机会到底怎么看</div>
                <div className="mt-2 text-sm leading-7 text-white/60">
                  当前关键词：`{keyword}`。下面这块是这次机会判断最核心的四层：市场、供应、利润、执行。
                </div>
              </div>
              <Badge variant="neutral">{opportunity.market}</Badge>
            </div>

            <div className="mt-5 space-y-4">
              <SectionCard
                title="1. 市场信号"
                rows={[
                  ["需求评分", `${opportunity.market_signal.demand_score}`],
                  ["趋势方向", opportunity.market_signal.trend_direction],
                  ["竞争强度", opportunity.market_signal.competition_level],
                  ["市场可信度", `${(opportunity.market_signal.confidence * 100).toFixed(0)}%`],
                ]}
              />
              <SectionCard
                title="2. 供应链确认"
                rows={[
                  ["供应商评分", `${opportunity.supplier_signal.supplier_score}`],
                  ["供货来源", opportunity.supplier_signal.supplier_source],
                  ["拿货成本", `${opportunity.supplier_signal.product_cost}`],
                  ["起订量 MOQ", `${opportunity.supplier_signal.MOQ}`],
                ]}
              />
              <SectionCard
                title="3. 利润验证"
                rows={[
                  ["预估售价", `${opportunity.profit_signal.expected_price}`],
                  ["毛利润", `${opportunity.profit_signal.gross_margin}`],
                  ["净利润率", `${opportunity.profit_signal.net_margin}%`],
                  ["利润可信度", `${(opportunity.profit_signal.profit_confidence * 100).toFixed(0)}%`],
                ]}
              />
              <SectionCard
                title="4. Shopify 动作"
                rows={[
                  ["店铺可执行", opportunity.execution.shopify_ready ? "可以" : "当前没有真实店铺商品信号"],
                  ["允许建草稿", opportunity.execution.draft_allowed ? "允许" : "不允许"],
                  ["允许直接发", opportunity.execution.publish_allowed ? "允许" : "不允许"],
                  ["当前平台动作", opportunity.shopify_action],
                ]}
              />
            </div>
          </Card>

          <div className="space-y-6">
            <Card className="border-white/8 bg-[#111A2E] p-6">
              <div className="text-sm font-medium text-white">现在建议你怎么做</div>
              <div className="mt-4 rounded-3xl border border-white/8 bg-white/5 p-5">
                <div className={`inline-flex rounded-full px-3 py-1 text-xs font-medium ${decisionChip(opportunity.decision)}`}>
                  {opportunity.decision}
                </div>
                <div className="mt-4 text-lg font-semibold text-white">{opportunitySummary}</div>
                <div className="mt-2 text-sm leading-7 text-white/60">
                  {buildActionCopy(opportunity.decision, opportunity.execution.draft_allowed, opportunity.execution.publish_allowed)}
                </div>
                <div className="mt-4 flex flex-wrap gap-3">
                  <Button asChild>
                    <a href={ROUTES.actionSuppliers}>去看供应链</a>
                  </Button>
                  <Button asChild variant="secondary">
                    <a href={ROUTES.actionLaunchQueue}>去看执行页</a>
                  </Button>
                </div>
              </div>
            </Card>

            <Card className="border-white/8 bg-[#111A2E] p-6">
              <div className="text-sm font-medium text-white">风险提醒</div>
              <div className="mt-4 space-y-3 text-sm text-white/70">
                {opportunity.risk_flags.length ? (
                  opportunity.risk_flags.map((item) => (
                    <div key={item} className="rounded-2xl border border-amber-400/15 bg-amber-400/10 px-4 py-3 text-amber-100">
                      {humanizeRisk(item)}
                    </div>
                  ))
                ) : (
                  <div className="rounded-2xl border border-emerald-400/15 bg-emerald-400/10 px-4 py-3 text-emerald-100">
                    当前这次机会没有额外风险标记。
                  </div>
                )}
              </div>
            </Card>

            <Card className="border-white/8 bg-[#111A2E] p-6">
              <div className="text-sm font-medium text-white">最近机会记录</div>
              <div className="mt-4 space-y-3">
                {history.items.length ? history.items.slice(0, 6).map((item) => (
                  <div key={item.id} className="rounded-2xl border border-white/8 bg-white/5 px-4 py-3">
                    <div className="flex items-center justify-between gap-3">
                      <div className="text-sm font-medium text-white">{item.keyword}</div>
                      <div className="text-xs text-white/40">{item.created_at || "无时间"}</div>
                    </div>
                    <div className="mt-2 grid gap-2 text-sm text-white/65 md:grid-cols-2">
                      <div>机会分：{item.opportunity_score}</div>
                      <div>决策：{item.decision}</div>
                      <div>执行结果：{item.execution_result || "还没执行"}</div>
                      <div>Shopify 动作：{item.shopify_action || "还没有"}</div>
                    </div>
                  </div>
                )) : <div className="text-sm text-white/55">还没有历史记录。</div>}
              </div>
              {latestHistory ? (
                <div className="mt-4 rounded-2xl border border-white/8 bg-black/10 px-4 py-3 text-sm text-white/55">
                  最新一条：{latestHistory.keyword}，机会分 {latestHistory.opportunity_score}，当前 {latestHistory.decision}。
                </div>
              ) : null}
            </Card>
          </div>
        </div>
      </div>
    </XBorderLayout>
  );
}

function Metric({
  title,
  value,
  desc,
  tone = "text-white",
}: {
  title: string;
  value: string;
  desc: string;
  tone?: string;
}) {
  return (
    <Card className="border-white/8 bg-[#111A2E] p-5">
      <div className="text-xs text-white/45">{title}</div>
      <div className={`mt-2 text-2xl font-semibold ${tone}`}>{value}</div>
      <div className="mt-2 text-sm leading-6 text-white/55">{desc}</div>
    </Card>
  );
}

function decisionToneClass(decision: string) {
  const normalized = String(decision || "").toUpperCase();
  if (normalized === "BUY" || normalized === "SCALE") return "border-emerald-400/20 bg-emerald-400/10";
  if (normalized === "TEST") return "border-[#4F7CFF]/20 bg-[#4F7CFF]/10";
  if (normalized === "WATCH") return "border-amber-400/20 bg-amber-400/10";
  return "border-rose-400/20 bg-rose-400/10";
}

function SectionCard({ title, rows }: { title: string; rows: Array<[string, string]> }) {
  return (
    <div className="rounded-2xl border border-white/8 bg-white/5 p-4">
      <div className="text-sm font-medium text-white">{title}</div>
      <div className="mt-3 space-y-2 text-sm text-white/70">
        {rows.map(([label, value]) => (
          <div key={label} className="flex items-start justify-between gap-3">
            <span className="text-white/45">{label}</span>
            <span className="text-right text-white">{value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function buildOpportunitySummary(decision: string) {
  const normalized = String(decision || "").toUpperCase();
  if (normalized === "BUY") return "这条机会已经通过市场、供应和利润三层判断，可以继续推进放量准备。";
  if (normalized === "TEST") return "这条机会值得先小步测试，先建 Shopify 草稿，再看真实反馈。";
  if (normalized === "WATCH") return "这条机会先观察，不建议马上投入上架动作。";
  return "这条机会当前不建议进入执行动作。";
}

function buildActionCopy(decision: string, draftAllowed: boolean, publishAllowed: boolean) {
  const normalized = String(decision || "").toUpperCase();
  if (normalized === "TEST") {
    return draftAllowed
      ? "当前适合先做 Shopify Draft。也就是先上草稿，不直接发布，先看后面的利润和反馈。"
      : "虽然现在是 TEST，但利润可信度还不够，先别直接建草稿。";
  }
  if (normalized === "BUY") {
    return publishAllowed
      ? "当前已经接近放量阶段，但系统仍然会先经过执行控制层，不会跳过安全闸门。"
      : "分数够了，但执行权限还没放开，所以现在还不能直接发布。";
  }
  if (normalized === "WATCH") return "先继续补市场或供应数据，再决定要不要推进。";
  return "当前先不要做执行动作，避免把不成熟商品推到店铺。";
}

function decisionTone(decision: string) {
  const normalized = String(decision || "").toUpperCase();
  if (normalized === "BUY") return "text-emerald-300";
  if (normalized === "TEST") return "text-amber-300";
  if (normalized === "WATCH") return "text-white/80";
  return "text-rose-300";
}

function decisionChip(decision: string) {
  const normalized = String(decision || "").toUpperCase();
  if (normalized === "BUY") return "bg-emerald-400/15 text-emerald-200";
  if (normalized === "TEST") return "bg-amber-400/15 text-amber-200";
  if (normalized === "WATCH") return "bg-white/10 text-white/80";
  return "bg-rose-400/15 text-rose-200";
}

function humanizeRisk(flag: string) {
  const mapper: Record<string, string> = {
    low_market_score: "市场分偏低，说明这个词现在不够强。",
    weak_supplier_score: "供应商质量不够稳，先别急着上量。",
    low_profit_margin: "利润率太薄，后面容易越卖越累。",
    high_competition: "竞争太密，进场后容易被卷价格。",
  };
  return mapper[flag] || flag;
}
