import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { P5Dashboard } from "@/components/p5/p5-dashboard";
import { P5Recommendations } from "@/components/p5/p5-recommendations";
import { ROUTES } from "@/config/routes";
import { TOKEN_KEY } from "@/lib/auth";
import { getServerLanguage } from "@/lib/i18n-server";

export default async function AIDiscoveryPage() {
  const lang = await getServerLanguage();
  const token = (await cookies()).get(TOKEN_KEY)?.value || "";
  if (!token) redirect(ROUTES.login);

  return (
    <XBorderLayout lang={lang} activePath="p5">
      <div className="space-y-6">
        <P5Dashboard lang={lang} />
        <P5Recommendations lang={lang} />
      </div>
    </XBorderLayout>
  );
}
