import Link from "next/link";
import { redirect } from "next/navigation";
import { cookies } from "next/headers";

import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { ProductList } from "@/components/products/product-list";
import { ActionCard, Button, Card, CardContent, InfoTile, SectionIntro } from "@/design-system/components";
import { ROUTES } from "@/config/routes";
import { getProducts, isAuthError } from "@/lib/api-gateway";
import { TOKEN_KEY } from "@/lib/auth";
import { t } from "@/lib/i18n";
import { getServerLanguage } from "@/lib/i18n-server";
import { ArrowRight } from "lucide-react";

export default async function ProductsPage({
  searchParams,
}: {
  searchParams?: Promise<{ search?: string }>;
}) {
  const lang = await getServerLanguage();
  const text = t(lang);
  const pageText = lang === "en"
    ? {
        total: "Total Products",
        current: "Current Module",
        module: "Products",
        back: "Back to Home",
      }
    : {
        total: "商品总量",
        current: "当前模块",
        module: "商品资产",
        back: "回到首页",
      };
  const cookieStore = await cookies();
  const token = cookieStore.get(TOKEN_KEY)?.value || "";
  if (!token) {
    redirect(ROUTES.login);
  }

  const resolvedSearchParams = searchParams ? await searchParams : undefined;
  const search = resolvedSearchParams?.search || "";

  const products = await getProducts(search, token).catch((error) => {
    if (isAuthError(error)) {
      redirect(ROUTES.login);
    }
    throw error;
  });

  return (
    <XBorderLayout lang={lang} activePath="products">
      <div className="space-y-6">
        <Card className="border-white/6 bg-[#111A2E] p-6 shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <CardContent className="p-0">
            <SectionIntro
              eyebrow="商品资产中心"
              title={text.productListTitle}
              description={text.productListBusinessDesc.replace("{count}", String(products.total))}
              action={(
                <Button asChild className="h-full bg-[#4F7CFF] hover:bg-[#4F7CFF]/90">
                  <Link href={ROUTES.home}>
                    {pageText.back}
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
              )}
            />
            <div className="mt-5 grid gap-4 md:grid-cols-3">
              <InfoTile label={pageText.total} value={String(products.total)} />
              <InfoTile label={pageText.current} value={pageText.module} />
              <InfoTile label="你现在要做的" value="挑出值得继续分析的商品" />
            </div>
          </CardContent>
        </Card>
        <div className="grid gap-4 md:grid-cols-3">
          <ActionCard title="先看市场" description="如果你还不确定方向，先回市场雷达页判断需求和趋势。" href={ROUTES.insights} label="去市场页" />
          <ActionCard title="看商业机会" description="如果你已经有方向，直接进机会页看利润、供应和风险。" href={ROUTES.insightsOpportunities} label="去机会页" />
          <ActionCard title="进采购池" description="如果你已经开始对比商品和货源，直接进采购池统一筛选。" href={ROUTES.actionProcurement} label="去采购池" />
        </div>
        <ProductList products={products.items} total={products.total} lang={lang} />
      </div>
    </XBorderLayout>
  );
}
