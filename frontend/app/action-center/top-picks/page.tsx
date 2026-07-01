import { redirect } from "next/navigation";
import { cookies } from "next/headers";

import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { OperationCenter } from "@/components/operation/operation-center";
import { TOKEN_KEY } from "@/lib/auth";
import { ROUTES } from "@/config/routes";
import { getServerLanguage } from "@/lib/i18n-server";

export default async function ActionTopPicksPage() {
  const token = (await cookies()).get(TOKEN_KEY)?.value || "";
  if (!token) redirect(ROUTES.login);
  const lang = await getServerLanguage();
  return (
    <XBorderLayout lang={lang} activePath="action">
      <OperationCenter lang={lang} />
    </XBorderLayout>
  );
}
