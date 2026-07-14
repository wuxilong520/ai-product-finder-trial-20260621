import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { ProcurementCenter } from "@/components/procurement/procurement-center";
import { ROUTES } from "@/config/routes";
import { TOKEN_KEY } from "@/lib/auth";
import { getServerLanguage } from "@/lib/i18n-server";

export default async function ProcurementPage({
  searchParams,
}: {
  searchParams?: Promise<{ keyword?: string }>;
}) {
  const token = (await cookies()).get(TOKEN_KEY)?.value || "";
  if (!token) redirect(ROUTES.login);

  const lang = await getServerLanguage();
  const resolvedSearchParams = searchParams ? await searchParams : undefined;
  const keyword = resolvedSearchParams?.keyword ? decodeURIComponent(String(resolvedSearchParams.keyword)) : "";

  return (
    <XBorderLayout lang={lang} activePath="action">
      <ProcurementCenter lang={lang} initialKeyword={keyword} />
    </XBorderLayout>
  );
}
