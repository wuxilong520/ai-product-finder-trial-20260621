import { MarketAnalysisCard } from "@/components/market/market-analysis-card";
import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { ActionCard, Card, CardContent, KpiTile, SectionIntro } from "@/design-system/components";
import { ROUTES } from "@/config/routes";
import { loadFlowPageData } from "@/lib/flow-page-data";

export default async function InsightsPage({
  searchParams,
}: {
  searchParams?: Promise<{ productId?: string; keyword?: string }>;
}) {
  const { lang } = await loadFlowPageData();
  const resolvedSearchParams = searchParams ? await searchParams : undefined;
  const productId = resolvedSearchParams?.productId;
  const keyword = resolvedSearchParams?.keyword ? decodeURIComponent(String(resolvedSearchParams.keyword)) : undefined;

  return (
    <XBorderLayout lang={lang} activePath="insights">
      <div className="space-y-6">
        <Card className="border-white/6 bg-[#111A2E]">
          <CardContent className="p-6">
            <SectionIntro
              eyebrow="商航AI · 市场雷达"
              title="先看这个方向有没有市场，再决定值不值得继续做"
              description="这页不是后台监控页，而是给普通用户看的市场雷达。你只需要看市场评分、需求趋势、竞争程度、商业机会和可信度，然后决定下一步。"
            />
            <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-5">
              <KpiTile label="市场评分" value="分析后生成" hint="看这个方向整体值不值得看" />
              <KpiTile label="需求趋势" value="分析后生成" hint="先看需求是涨是跌" />
              <KpiTile label="竞争程度" value="分析后生成" hint="判断是不是太卷了" />
              <KpiTile label="商业机会" value="分析后生成" hint="看要不要继续进采购池" />
              <KpiTile label="可信度" value="分析后生成" hint="来源越真实，结论越能信" />
            </div>
          </CardContent>
        </Card>

        <div className="grid gap-4 md:grid-cols-3">
          <ActionCard
            title="市场结果不错"
            description="继续进入商品机会页，从方向里筛更值得做的单品。"
            href={ROUTES.insightsOpportunities}
            label="进入商品机会页"
          />
          <ActionCard
            title="单品有机会"
            description="继续去看 1688 货源、价格、评分、MOQ 和发货周期。"
            href={ROUTES.actionSuppliers}
            label="进入供应链页"
          />
          <ActionCard
            title="方向已经能落地"
            description="最后进入利润决策页，看值不值得测试上架。"
            href={ROUTES.actionProfit}
            label="进入利润决策页"
          />
        </div>

        <MarketAnalysisCard lang={lang} initialKeyword={keyword || (productId ? String(productId) : undefined)} />
      </div>
    </XBorderLayout>
  );
}
