import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { SupplierCenter } from "@/components/supplier/supplier-center";
import { ROUTES } from "@/config/routes";
import { TOKEN_KEY } from "@/lib/auth";
import { getServerLanguage } from "@/lib/i18n-server";

export default async function SupplierPage() {
  const lang = await getServerLanguage();
  const token = (await cookies()).get(TOKEN_KEY)?.value || "";
  if (!token) redirect(ROUTES.login);

  return (
    <XBorderLayout lang={lang} activePath="supplier">
      <SupplierCenter lang={lang} />
    </XBorderLayout>
  );
}
