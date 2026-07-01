import { redirect } from "next/navigation";
import { cookies } from "next/headers";

import { HonestStatusPage } from "@/components/shared/honest-status-page";
import { ROUTES } from "@/config/routes";
import { TOKEN_KEY } from "@/lib/auth";
import { getServerLanguage } from "@/lib/i18n-server";

export default async function SettingsProfilePage() {
  const token = (await cookies()).get(TOKEN_KEY)?.value || "";
  if (!token) redirect(ROUTES.login);
  const lang = await getServerLanguage();
  return (
    <HonestStatusPage
      lang={lang}
      activePath="settings"
      title="账号信息"
      description="账号信息现在有独立页面了，不再和其他设置堆在一起。"
      statusLabel="页面状态"
      statusValue="已独立可访问"
      currentLabel="当前可用"
      currentValue="查看当前账号、套餐、订单和使用状态"
      nextLabel="后续补齐"
      nextValue="补用户资料编辑、头像、团队信息等"
    />
  );
}
