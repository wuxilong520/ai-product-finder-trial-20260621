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
        <Card className="border-white/6 bg-[linear-gradient(135deg,rgba(79,124,255,0.14),rgba(17,26,46,0.96))]">
          <CardContent className="p-6">
            <SectionIntro
              eyebrow="商航AI · 市场分析"
              title="先判断这个方向有没有机会，再决定要不要继续深挖"
              description="这页是趋势判断页，不是后台监控页。你重点只看 5 件事：市场机会指数、需求趋势、竞争热度、进入难度、数据可信度。"
            />
            <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-5">
              <KpiTile label="市场机会指数" value="分析后生成" hint="先看这个方向值不值得继续花时间" />
              <KpiTile label="需求趋势" value="分析后生成" hint="先看需求是涨是跌" />
              <KpiTile label="竞争热度" value="分析后生成" hint="判断这个赛道是不是已经太卷" />
              <KpiTile label="进入难度" value="分析后生成" hint="判断新手切进去会不会太难" />
              <KpiTile label="数据可信度" value="分析后生成" hint="来源越真实，结论越值得信" />
            </div>
          </CardContent>
        </Card>

        <div className="grid gap-4 md:grid-cols-3">
          <ActionCard
            title="继续看商品榜单"
            description="如果方向不错，下一步就去榜单里挑更值得深挖的具体商品。"
            href={ROUTES.insightsOpportunities}
            label="进入商品机会榜"
          />
          <ActionCard
            title="继续看供应方案"
            description="如果你已经想开始找货，就继续去看价格、MOQ、稳定性和风险。"
            href={ROUTES.actionSuppliers}
            label="进入供应方案页"
          />
          <ActionCard
            title="继续看利润判断"
            description="最后统一看利润空间、风险和 AI 进入建议。"
            href={ROUTES.actionProfit}
            label="进入利润判断页"
          />
        </div>

        <MarketAnalysisCard lang={lang} initialKeyword={keyword || (productId ? String(productId) : undefined)} />
      </div>
    </XBorderLayout>
  );
}
