import { redirect } from "next/navigation";
import { cookies } from "next/headers";

import { HonestStatusPage } from "@/components/shared/honest-status-page";
import { ROUTES } from "@/config/routes";
import { TOKEN_KEY } from "@/lib/auth";
import { getServerLanguage } from "@/lib/i18n-server";

export default async function StoreLinksPage() {
  const token = (await cookies()).get(TOKEN_KEY)?.value || "";
  if (!token) redirect(ROUTES.login);
  const lang = await getServerLanguage();
  return (
    <HonestStatusPage
      lang={lang}
      activePath="settings"
      title="店铺绑定"
      description="这里单独作为店铺绑定页面存在。当前还没有接真实店铺平台，所以先不装成可绑定成功。"
      statusLabel="接入状态"
      statusValue="待真实平台接入"
      currentLabel="当前可用"
      currentValue="查看账号订阅和后续接入准备状态"
      nextLabel="后续补齐"
      nextValue="接入 Amazon / Shopify / 1688 等真实店铺连接"
    />
  );
}
