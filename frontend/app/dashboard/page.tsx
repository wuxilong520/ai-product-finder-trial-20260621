import { redirect } from "next/navigation";
import { cookies } from "next/headers";

import { ROUTES } from "@/config/routes";
import { NewDashboard } from "@/modules/dashboard/new-dashboard";
import { OldDashboard } from "@/modules/dashboard/old-dashboard";
import { getProducts, isAuthError, isNewDashboardEnabled } from "@/lib/api";
import { TOKEN_KEY } from "@/lib/auth";
import { t } from "@/lib/i18n";
import { getServerLanguage } from "@/lib/i18n-server";

export default async function DashboardPage({
  searchParams
}: {
  searchParams?: Promise<{ search?: string }>;
}) {
  console.log("[dashboard] start");
  const lang = await getServerLanguage();
  console.log("[dashboard] lang", lang);
  const text = t(lang);
  const cookieStore = await cookies();
  console.log("[dashboard] cookies ready");
  const token = cookieStore.get(TOKEN_KEY)?.value || "";
  if (!token) {
    console.log("[dashboard] no token, redirect");
    redirect(ROUTES.login);
  }

  const resolvedSearchParams = searchParams ? await searchParams : undefined;
  const search = resolvedSearchParams?.search || "";
  console.log("[dashboard] search", search);
  let data;
  try {
    console.log("[dashboard] getProducts before");
    data = await getProducts(search, token);
    console.log("[dashboard] getProducts after", data?.total);
  } catch (error) {
    console.log("[dashboard] getProducts error", error);
    if (isAuthError(error)) {
      console.log("[dashboard] auth error, redirect");
      redirect(ROUTES.login);
    }
    throw error;
  }

  console.log("[dashboard] render");
  if (isNewDashboardEnabled()) {
    return <NewDashboard token={token} lang={lang} />;
  }

  return <OldDashboard lang={lang} data={data} />;
}
