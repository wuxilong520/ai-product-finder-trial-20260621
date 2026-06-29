import Link from "next/link";
import { redirect } from "next/navigation";
import { cookies } from "next/headers";

import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { ProductList } from "@/components/products/product-list";
import { Button, Card, InfoTile } from "@/design-system/components";
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
          <div className="flex flex-col gap-6 xl:flex-row xl:items-end xl:justify-between">
            <div>
              <div className="mb-3 inline-flex rounded-full border border-[#4F7CFF]/20 bg-[#4F7CFF]/10 px-3 py-1 text-xs font-medium text-[#4F7CFF]">
                商品资产中心
              </div>
              <h1 className="text-[28px] font-bold tracking-tight text-white">{text.productListTitle}</h1>
              <p className="mt-3 max-w-2xl text-sm leading-7 text-white/56">
                {text.productListBusinessDesc.replace("{count}", String(products.total))}
              </p>
            </div>
            <div className="grid gap-4 md:grid-cols-3 xl:min-w-[760px]">
              <InfoTile label="商品总量" value={String(products.total)} />
              <InfoTile label="当前模块" value="商品资产" />
              <Button asChild className="h-full bg-[#4F7CFF] hover:bg-[#4F7CFF]/90">
                <Link href={ROUTES.dashboard}>
                  回到首页驾驶舱
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </div>
          </div>
        </Card>
        <ProductList products={products.items} total={products.total} lang={lang} />
      </div>
    </XBorderLayout>
  );
}
