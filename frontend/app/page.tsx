import { redirect } from "next/navigation";
import { cookies } from "next/headers";

import { ROUTES } from "@/config/routes";
import { getCurrentUser, isAuthError } from "@/lib/api-gateway";
import { NewDashboard } from "@/modules/dashboard/new-dashboard";
import { TOKEN_KEY } from "@/lib/auth";
import { getServerLanguage } from "@/lib/i18n-server";
import { PublicHomeShell } from "@/components/marketing/public-home-shell";

export default async function HomePage() {
  const lang = await getServerLanguage();
  const token = (await cookies()).get(TOKEN_KEY)?.value || "";

  if (!token) {
    return <PublicHomeShell lang={lang} />;
  }

  try {
    await getCurrentUser(token);
  } catch (error) {
    if (isAuthError(error)) {
      return <PublicHomeShell lang={lang} />;
    }
    throw error;
  }

  return <NewDashboard token={token} lang={lang} />;
}
