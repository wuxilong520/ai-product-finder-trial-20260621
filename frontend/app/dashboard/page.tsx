import { redirect } from "next/navigation";
import { cookies } from "next/headers";

import { AppShell } from "@/components/app-shell";
import { ProductList } from "@/components/products/product-list";
import { PageHero } from "@/design-system/components";
import { getProducts } from "@/lib/api";
import { TOKEN_KEY } from "@/lib/auth";
import { t } from "@/lib/i18n";
import { getServerLanguage } from "@/lib/i18n-server";

export default async function DashboardPage({
  searchParams
}: {
  searchParams?: Promise<{ search?: string }>;
}) {
  const lang = await getServerLanguage();
  const text = t(lang);
  const cookieStore = await cookies();
  const token = cookieStore.get(TOKEN_KEY)?.value || "";
  if (!token) {
    redirect("/login");
  }

  const resolvedSearchParams = searchParams ? await searchParams : undefined;
  const search = resolvedSearchParams?.search || "";
  const data = await getProducts(search, token);

  return (
    <AppShell lang={lang}>
      <PageHero
        eyebrow={text.dashboardEyebrow}
        title={text.dashboardTitle}
        description={text.dashboardDesc}
        action={<div className="rounded-full border border-app-border bg-white/8 px-4 py-2 text-sm text-app-text-secondary shadow-app-soft">{text.dashboardCount.replace("{count}", String(data.total))}</div>}
      />
      <ProductList products={data.items} total={data.total} lang={lang} />
    </AppShell>
  );
}
