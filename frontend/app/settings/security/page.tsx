import { redirect } from "next/navigation";
import { cookies } from "next/headers";

import { HonestStatusPage } from "@/components/shared/honest-status-page";
import { ROUTES } from "@/config/routes";
import { TOKEN_KEY } from "@/lib/auth";
import { getServerLanguage } from "@/lib/i18n-server";

export default async function SettingsSecurityPage() {
  const token = (await cookies()).get(TOKEN_KEY)?.value || "";
  if (!token) redirect(ROUTES.login);
  const lang = await getServerLanguage();
  return (
    <HonestStatusPage
      lang={lang}
      activePath="settings"
      title="密码与安全"
      description="密码与安全入口已经独立。当前真实可用的是邮箱验证码登录和忘记密码流程。"
      statusLabel="当前可用"
      statusValue="邮箱验证码登录 / 忘记密码"
      currentLabel="现在能做什么"
      currentValue="通过登录页或忘记密码页完成安全验证"
      nextLabel="后续补齐"
      nextValue="补登录设备管理、异常提醒、二次验证"
    />
  );
}
