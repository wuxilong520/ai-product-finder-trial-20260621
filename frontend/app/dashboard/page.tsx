import { redirect } from "next/navigation";
import { cookies } from "next/headers";

import { ROUTES } from "@/config/routes";
import { NewDashboard } from "@/modules/dashboard/new-dashboard";
import { getProducts, isAuthError, isNewDashboardEnabled } from "@/lib/api";
import { TOKEN_KEY } from "@/lib/auth";
import { t } from "@/lib/i18n";
import { getServerLanguage } from "@/lib/i18n-server";

export default async function DashboardPage({
  searchParams
}: {
  searchParams?: Promise<{ search?: string }>;
}) {
  const lang = await getServerLanguage();
  const cookieStore = await cookies();
  const token = cookieStore.get(TOKEN_KEY)?.value || "";
  if (!token) {
    redirect(ROUTES.login);
  }

  if (isNewDashboardEnabled()) {
    return <NewDashboard token={token} lang={lang} />;
  }

  const resolvedSearchParams = searchParams ? await searchParams : undefined;
  const search = resolvedSearchParams?.search || "";
  try {
    await getProducts(search, token);
  } catch (error) {
    if (isAuthError(error)) {
      redirect(ROUTES.login);
    }
    throw error;
  }

  return <NewDashboard token={token} lang={lang} />;
}
