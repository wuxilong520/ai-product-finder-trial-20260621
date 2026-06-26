import { redirect } from "next/navigation";
import { cookies } from "next/headers";

import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { ProductDetail } from "@/components/products/product-detail";
import { MarketAnalysisCard } from "@/components/market/market-analysis-card";
import { Card } from "@/design-system/components";
import { ROUTES } from "@/config/routes";
import { getProduct, isAuthError } from "@/lib/api";
import { TOKEN_KEY } from "@/lib/auth";
import { t } from "@/lib/i18n";
import { getServerLanguage } from "@/lib/i18n-server";

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
        </Card>
        <ProductDetail product={product} analysisReport={null} lang={lang} />
        <MarketAnalysisCard lang={lang} initialKeyword={product.title_zh || product.title} />
      </div>
    </XBorderLayout>
  );
}
