import { redirect } from "next/navigation";
import { cookies } from "next/headers";
import Link from "next/link";

import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { Card, CardContent, CardHeader, CardTitle, InfoTile, Button } from "@/design-system/components";
import { ROUTES } from "@/config/routes";
import { TOKEN_KEY } from "@/lib/auth";
import { getCurrentUser } from "@/lib/api";
import { getServerLanguage } from "@/lib/i18n-server";

export default async function SettingsSecurityPage() {
  const token = (await cookies()).get(TOKEN_KEY)?.value || "";
  if (!token) redirect(ROUTES.login);
  const lang = await getServerLanguage();
  const user = await getCurrentUser(token);
  return (
    <XBorderLayout lang={lang} activePath="settings">
      <div className="space-y-6">
        <Card className="border-white/8 bg-[#121c2c] p-6 shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <h1 className="text-3xl font-semibold tracking-tight text-white">密码与安全</h1>
          <p className="mt-2 text-sm leading-7 text-white/60">
            这里现在直接给你可用的安全入口：密码登录、邮箱验证码登录、忘记密码。
          </p>
        </Card>

        <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
          <Card className="border-white/8 bg-[#121c2c]">
            <CardHeader><CardTitle>登录邮箱</CardTitle></CardHeader>
            <CardContent><InfoTile label="当前账号" value={user.email} /></CardContent>
          </Card>
          <Card className="border-white/8 bg-[#121c2c]">
            <CardHeader><CardTitle>密码登录</CardTitle></CardHeader>
            <CardContent><InfoTile label="当前状态" value="已启用" /></CardContent>
          </Card>
          <Card className="border-white/8 bg-[#121c2c]">
            <CardHeader><CardTitle>验证码登录</CardTitle></CardHeader>
            <CardContent><InfoTile label="当前状态" value="已启用" /></CardContent>
          </Card>
          <Card className="border-white/8 bg-[#121c2c]">
            <CardHeader><CardTitle>找回密码</CardTitle></CardHeader>
            <CardContent><InfoTile label="当前状态" value="已启用" /></CardContent>
          </Card>
        </div>

        <Card className="border-white/8 bg-[#121c2c]">
          <CardHeader>
            <CardTitle>现在能直接做的安全操作</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm text-white/70">
            <div className="rounded-2xl border border-white/8 bg-white/5 p-4">
              1. 如果你只是想登录，可以直接去登录页，选择“密码登录”或“验证码登录”。
            </div>
            <div className="rounded-2xl border border-white/8 bg-white/5 p-4">
              2. 如果你忘记密码，可以直接走“忘记密码”流程，用邮箱验证码重设。
            </div>
            <div className="rounded-2xl border border-white/8 bg-white/5 p-4">
              3. 现在还没做登录设备管理和二次验证，后面我会继续补到这里。
            </div>
          </CardContent>
        </Card>

        <div className="flex flex-wrap gap-3">
          <Button asChild><Link href={ROUTES.login}>去登录页</Link></Button>
          <Button asChild variant="secondary"><Link href={ROUTES.forgotPassword}>去忘记密码</Link></Button>
        </div>
      </div>
    </XBorderLayout>
  );
}
