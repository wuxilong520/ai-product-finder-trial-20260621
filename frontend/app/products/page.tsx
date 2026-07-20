import Link from "next/link";
import { redirect } from "next/navigation";
import { cookies } from "next/headers";

import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { ProductList } from "@/components/products/product-list";
import { ActionCard, Button, Card, CardContent, EmptyState, InfoTile, SectionIntro, StatusAlert } from "@/design-system/components";
import { ROUTES } from "@/config/routes";
import { getProducts, isAuthError } from "@/lib/api-gateway";
import { TOKEN_KEY } from "@/lib/auth";
import { getServerLanguage } from "@/lib/i18n-server";
import { ArrowRight } from "lucide-react";

export default async function ProductsPage({
  searchParams,
}: {
  searchParams?: Promise<{ search?: string }>;
}) {
  const lang = await getServerLanguage();
  const pageText = lang === "en"
    ? {
        total: "Total products",
        current: "Current stage",
        module: "Opportunity board",
        back: "Back to Home",
      }
    : {
        total: "商品总量",
        current: "当前阶段",
        module: "商品机会榜",
        back: "回到首页",
      };
  const cookieStore = await cookies();
  const token = cookieStore.get(TOKEN_KEY)?.value || "";
  if (!token) {
    redirect(ROUTES.login);
  }

  const resolvedSearchParams = searchParams ? await searchParams : undefined;
  const search = resolvedSearchParams?.search || "";

  let loadError: string | null = null;
  const products = await getProducts(search, token).catch((error) => {
    if (isAuthError(error)) {
      redirect(ROUTES.login);
    }
    loadError = error instanceof Error ? error.message : "商品列表暂时打不开";
    return { items: [], total: 0 };
  });

  return (
    <XBorderLayout lang={lang} activePath="products">
      <div className="space-y-6">
        <Card className="border-white/6 bg-[#111A2E] p-6 shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <CardContent className="p-0">
            <SectionIntro
              eyebrow="商航AI · 商品榜单"
              title="把真实商品变成可筛选、可比较、可继续分析的机会榜单"
              description={`当前已进入系统的真实商品 ${products.total} 个。这里不再像后台表格，而是按商品机会、利润空间和下一步动作来组织。`}
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
              <InfoTile label="你现在要做的" value="挑出值得继续分析和采购的商品" />
            </div>
          </CardContent>
        </Card>
        <div className="grid gap-4 md:grid-cols-3">
          <ActionCard title="先看市场分析" description="如果方向还没定，先回趋势页判断需求和机会。" href={ROUTES.insights} label="去市场分析" />
          <ActionCard title="看机会榜单" description="如果你已经有方向，继续去看更强的机会商品。" href={ROUTES.insightsOpportunities} label="去机会榜" />
          <ActionCard title="做采购方案" description="如果你已经开始比货源，就去看价格、MOQ 和供应稳定性。" href={ROUTES.actionProcurement} label="去采购方案" />
        </div>
        {loadError ? (
          <Card className="border-white/8 bg-[#121c2c]">
            <CardContent className="p-6">
              <StatusAlert status="warning" message={`商品列表接口暂时失败：${loadError}`} />
              <div className="mt-4">
                <EmptyState text="页面已经保护住了，没有直接崩溃。你可以先回市场分析页，或者稍后再刷新。" />
              </div>
            </CardContent>
          </Card>
        ) : (
          <ProductList products={products.items} total={products.total} lang={lang} />
        )}
      </div>
    </XBorderLayout>
  );
}
