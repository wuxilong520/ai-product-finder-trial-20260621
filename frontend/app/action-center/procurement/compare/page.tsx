import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { ProcurementCompareCenter } from "@/components/procurement/procurement-compare-center";
import { ROUTES } from "@/config/routes";
import { TOKEN_KEY } from "@/lib/auth";
import { getServerLanguage } from "@/lib/i18n-server";

export default async function ProcurementComparePage({
  searchParams,
}: {
  searchParams?: Promise<{ ids?: string }>;
}) {
  const token = (await cookies()).get(TOKEN_KEY)?.value || "";
  if (!token) redirect(ROUTES.login);

  const lang = await getServerLanguage();
  const resolvedSearchParams = searchParams ? await searchParams : undefined;
  const ids = String(resolvedSearchParams?.ids || "")
    .split(",")
    .map((value) => Number(value.trim()))
    .filter((value) => Number.isInteger(value) && value > 0);

  return (
    <XBorderLayout lang={lang} activePath="action">
      <ProcurementCompareCenter ids={ids} />
    </XBorderLayout>
  );
}
