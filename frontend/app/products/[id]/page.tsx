import { redirect } from "next/navigation";
import { cookies } from "next/headers";

import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { ProductDetail } from "@/components/products/product-detail";
import { MarketAnalysisCard } from "@/components/market/market-analysis-card";
import { Button, Card, InfoTile } from "@/design-system/components";
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
          <h1 className="text-3xl font-semibold tracking-tight text-white">{text.productDetailTitle}</h1>
          <p className="mt-2 max-w-2xl text-sm leading-7 text-white/60">{text.productDetailDesc}</p>
          <div className="mt-5 grid gap-4 md:grid-cols-3">
            <InfoTile label="流程位置" value="商品详情 / 决策准备区" />
            <InfoTile label="下一步建议" value="看完详情后进入市场或执行" />
            <Button asChild className="h-full">
              <Link href={ROUTES.dashboard}>
                返回主决策流
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </div>
        </Card>
        <ProductDetail product={product} analysisReport={null} lang={lang} />
        <MarketAnalysisCard lang={lang} initialKeyword={product.title_zh || product.title} />
      </div>
    </XBorderLayout>
  );
}
