import { redirect } from "next/navigation";
import { cookies } from "next/headers";

import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { ProductDetail } from "@/components/products/product-detail";
import { MarketAnalysisCard } from "@/components/market/market-analysis-card";
import { ActionCard, Button, Card, CardContent, EmptyState, InfoTile, SectionIntro, StatusAlert } from "@/design-system/components";
import { ROUTES } from "@/config/routes";
import { getProduct, isAuthError } from "@/lib/api-gateway";
import { TOKEN_KEY } from "@/lib/auth";
import { getServerLanguage } from "@/lib/i18n-server";
import Link from "next/link";
import { ArrowRight } from "lucide-react";

export default async function ProductDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const lang = await getServerLanguage();
  const pageText = lang === "en"
    ? {
        flow: "Current stage",
        flowValue: "Product report / decision prep",
        next: "Next suggestion",
        nextValue: "Review report, then continue market or sourcing",
        back: "Back to Home",
      }
    : {
        flow: "当前阶段",
        flowValue: "商品报告 / 决策准备",
        next: "下一步建议",
        nextValue: "看完报告后继续市场分析或供应方案",
        back: "返回首页",
      };
  const cookieStore = await cookies();
  const token = cookieStore.get(TOKEN_KEY)?.value || "";
  if (!token) {
    redirect(ROUTES.login);
  }

  const resolvedParams = await params;
  let product;
  let loadError: string | null = null;
  try {
    product = await getProduct(resolvedParams.id, token);
  } catch (error) {
    if (isAuthError(error)) {
      redirect(ROUTES.login);
    }
    loadError = error instanceof Error ? error.message : "商品详情暂时打不开";
  }
  return (
    <XBorderLayout lang={lang} activePath="products">
      <div className="space-y-6">
        <Card className="border-white/8 bg-[linear-gradient(180deg,rgba(255,255,255,0.04),rgba(255,255,255,0.02))] p-5 shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <CardContent className="p-0">
            <SectionIntro
              eyebrow="商航AI · AI商业分析报告"
              title="把一个商品讲清楚：能不能做、为什么、下一步去哪里"
              description="这一页不再像后台详情页，而是把商品机会、利润空间、供应链方向和下一步动作讲清楚。"
              action={(
                <Button asChild className="h-11">
                  <Link href={ROUTES.home}>
                    {pageText.back}
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
              )}
            />
            <div className="mt-5 grid gap-4 md:grid-cols-3">
              <InfoTile label={pageText.flow} value={pageText.flowValue} />
              <InfoTile label={pageText.next} value={pageText.nextValue} />
              <InfoTile label="当前商品" value={product ? (product.title_zh || product.title) : "暂时未读取到"} />
            </div>
          </CardContent>
        </Card>
        {product ? <div className="grid gap-4 md:grid-cols-3">
          <ActionCard title="查看市场分析" description="先确认这个商品在海外市场有没有真实需求和趋势。" href={`${ROUTES.insights}?keyword=${encodeURIComponent(product.title_zh || product.title)}`} label="去看市场分析" />
          <ActionCard title="进入采购方案" description="如果你想继续推进，就去统一比较价格、利润和风险。" href={`${ROUTES.actionProcurement}?keyword=${encodeURIComponent(product.title_zh || product.title)}`} label="去看采购方案" />
          <ActionCard title="查看供应方案" description="继续对比货源、成本、MOQ 和供应稳定性。" href={`${ROUTES.actionSuppliers}?keyword=${encodeURIComponent(product.title_zh || product.title)}`} label="去看供应方案" />
        </div> : null}
        {loadError || !product ? (
          <Card className="border-white/8 bg-[#121c2c]">
            <CardContent className="p-6">
              <StatusAlert status="warning" message={loadError || "商品详情暂时不可用"} />
              <div className="mt-4">
                <EmptyState text="报告页已经保护住了。虽然数据没回来，但页面不会直接崩溃。" />
              </div>
            </CardContent>
          </Card>
        ) : (
          <>
            <ProductDetail product={product} analysisReport={null} lang={lang} />
            <MarketAnalysisCard lang={lang} initialKeyword={product.title_zh || product.title} />
          </>
        )}
      </div>
    </XBorderLayout>
  );
}
