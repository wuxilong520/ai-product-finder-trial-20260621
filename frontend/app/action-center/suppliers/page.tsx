import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { SupplierCenter } from "@/components/supplier/supplier-center";
import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { ROUTES } from "@/config/routes";
import { TOKEN_KEY } from "@/lib/auth";
import { getServerLanguage } from "@/lib/i18n-server";

export default async function SupplierPicksPage({
  searchParams,
}: {
  searchParams?: Promise<{ keyword?: string; category?: string }>;
}) {
  const token = (await cookies()).get(TOKEN_KEY)?.value || "";
  if (!token) redirect(ROUTES.login);

  const lang = await getServerLanguage();
  const resolvedSearchParams = searchParams ? await searchParams : undefined;
  const keyword = resolvedSearchParams?.keyword ? decodeURIComponent(String(resolvedSearchParams.keyword)) : "";
  const category = resolvedSearchParams?.category ? decodeURIComponent(String(resolvedSearchParams.category)) : "";

  return (
    <XBorderLayout lang={lang} activePath="action">
      <SupplierCenter lang={lang} initialKeyword={keyword} initialCategory={category} />
    </XBorderLayout>
  );
}
