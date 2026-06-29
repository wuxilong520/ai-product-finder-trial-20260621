import Link from "next/link";
import { redirect } from "next/navigation";
import { cookies } from "next/headers";

import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { ProductList } from "@/components/products/product-list";
import { Badge, Button, Card, InfoTile } from "@/design-system/components";
import { ROUTES } from "@/config/routes";
import { getProducts, isAuthError } from "@/lib/api";
import { TOKEN_KEY } from "@/lib/auth";
import { t } from "@/lib/i18n";
import { getServerLanguage } from "@/lib/i18n-server";
import { ArrowRight, PackageSearch, Sparkles } from "lucide-react";

export default async function ProductsPage({
  searchParams,
}: {
  searchParams?: Promise<{ search?: string }>;
}) {
  const lang = await getServerLanguage();
  const text = t(lang);
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
      <div className="space-y-5">
        <Card className="border-white/8 bg-[linear-gradient(180deg,rgba(255,255,255,0.04),rgba(255,255,255,0.02))] p-5 shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <div className="flex flex-wrap items-center gap-3">
            <Badge variant="brand" className="px-4 py-2 text-sm font-medium">
              <PackageSearch className="h-4 w-4" />
              {text.productZone}
            </Badge>
            <Badge variant="neutral" className="px-4 py-2 text-sm text-app-text-secondary">
              <Sparkles className="h-4 w-4 text-app-brand-secondary" />
              {text.unifiedStyle}
            </Badge>
          </div>
          <h1 className="mt-4 text-3xl font-semibold tracking-tight text-white">{text.productListTitle}</h1>
          <p className="mt-2 max-w-2xl text-sm leading-7 text-white/60">
            {text.productListBusinessDesc.replace("{count}", String(products.total))}
          </p>
          <div className="mt-5 grid gap-4 md:grid-cols-3">
            <InfoTile label="当前定位" value="商品中心（辅助页面）" />
            <InfoTile label="在流程中的作用" value="沉淀商品，进入分析与决策" />
            <Button asChild className="h-full">
              <Link href={ROUTES.dashboard}>
                返回主决策流
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </div>
        </Card>
        <ProductList products={products.items} total={products.total} lang={lang} />
      </div>
    </XBorderLayout>
  );
}
