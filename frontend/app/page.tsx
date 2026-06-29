import { redirect } from "next/navigation";
import { cookies } from "next/headers";

import { ROUTES } from "@/config/routes";
import { NewDashboard } from "@/modules/dashboard/new-dashboard";
import { TOKEN_KEY } from "@/lib/auth";
import { getServerLanguage } from "@/lib/i18n-server";

export default async function HomePage() {
  const lang = await getServerLanguage();
  const token = (await cookies()).get(TOKEN_KEY)?.value || "";

  if (!token) {
    redirect(ROUTES.login);
  }

  return <NewDashboard token={token} lang={lang} />;
}
