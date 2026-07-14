import { redirect } from "next/navigation";
import { cookies } from "next/headers";

import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { ProductDetail } from "@/components/products/product-detail";
import { MarketAnalysisCard } from "@/components/market/market-analysis-card";
import { ActionCard, Button, Card, CardContent, InfoTile, SectionIntro } from "@/design-system/components";
import { ROUTES } from "@/config/routes";
import { getProduct, isAuthError } from "@/lib/api-gateway";
import { TOKEN_KEY } from "@/lib/auth";
import { t } from "@/lib/i18n";
import { getServerLanguage } from "@/lib/i18n-server";
import Link from "next/link";
import { ArrowRight } from "lucide-react";

export default async function ProductDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const lang = await getServerLanguage();
  const text = t(lang);
  const pageText = lang === "en"
    ? {
        flow: "Flow Position",
        flowValue: "Product Detail / Decision Prep",
        next: "Next Suggestion",
        nextValue: "Review details, then open insights or action center",
        back: "Back to Home",
      }
    : {
        flow: "流程位置",
        flowValue: "商品详情 / 决策准备区",
        next: "下一步建议",
        nextValue: "看完详情后进入市场或执行",
        back: "返回首页",
      };
  const cookieStore = await cookies();
  const token = cookieStore.get(TOKEN_KEY)?.value || "";
  if (!token) {
    redirect(ROUTES.login);
  }

  const resolvedParams = await params;
  let product;
  try {
    product = await getProduct(resolvedParams.id, token);
  } catch (error) {
    if (isAuthError(error)) {
      redirect(ROUTES.login);
    }
    throw error;
  }
  return (
    <XBorderLayout lang={lang} activePath="products">
      <div className="space-y-6">
        <Card className="border-white/8 bg-[linear-gradient(180deg,rgba(255,255,255,0.04),rgba(255,255,255,0.02))] p-5 shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <CardContent className="p-0">
            <SectionIntro
              eyebrow="商航AI · 商品详情"
              title={text.productDetailTitle}
              description={text.productDetailDesc}
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
              <InfoTile label="当前商品" value={product.title_zh || product.title} />
            </div>
          </CardContent>
        </Card>
        <div className="grid gap-4 md:grid-cols-3">
          <ActionCard title="查看市场分析" description="先确认这个商品在海外市场有没有需求和机会。" href={`${ROUTES.insights}?keyword=${encodeURIComponent(product.title_zh || product.title)}`} label="去看市场" />
          <ActionCard title="进入采购池" description="如果你想把这个方向继续推进，就进采购池统一比较。 " href={`${ROUTES.actionProcurement}?keyword=${encodeURIComponent(product.title_zh || product.title)}`} label="去采购池" />
          <ActionCard title="查看供应链" description="继续对比 1688 货源、成本、MOQ 和风险。" href={`${ROUTES.actionSuppliers}?keyword=${encodeURIComponent(product.title_zh || product.title)}`} label="去看供应链" />
        </div>
        <ProductDetail product={product} analysisReport={null} lang={lang} />
        <MarketAnalysisCard lang={lang} initialKeyword={product.title_zh || product.title} />
      </div>
    </XBorderLayout>
  );
}
