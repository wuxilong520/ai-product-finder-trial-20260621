import { redirect } from "next/navigation";
import { cookies } from "next/headers";

import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { Card, CardContent, CardHeader, CardTitle, InfoTile } from "@/design-system/components";
import { ROUTES } from "@/config/routes";
import { TOKEN_KEY } from "@/lib/auth";
import { getServerLanguage } from "@/lib/i18n-server";

export default async function SettingsPage() {
  const lang = await getServerLanguage();
  const token = (await cookies()).get(TOKEN_KEY)?.value || "";

  if (!token) {
    redirect(ROUTES.login);
  }

  return (
    <XBorderLayout lang={lang} activePath="settings">
      <div className="space-y-6">
        <Card className="border-white/8 bg-[#121c2c] p-6 shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <h1 className="text-3xl font-semibold tracking-tight text-white">账户设置</h1>
          <p className="mt-2 text-sm leading-7 text-white/60">
            这里统一管理店铺绑定、账号信息和登录密码，不展示任何技术配置。
          </p>
        </Card>

        <div className="grid gap-6 xl:grid-cols-3">
          <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <CardTitle>店铺绑定</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <InfoTile label="当前状态" value="可管理" />
              <InfoTile label="店铺数量" value="待接入展示" />
            </CardContent>
          </Card>

          <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <CardTitle>账号信息</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <InfoTile label="账户类型" value="正式账户" />
              <InfoTile label="使用状态" value="正常" />
            </CardContent>
          </Card>

          <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <CardTitle>登录密码修改</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <InfoTile label="安全状态" value="已启用" />
              <InfoTile label="修改入口" value="即将接入当前页" />
            </CardContent>
          </Card>
        </div>
      </div>
    </XBorderLayout>
  );
}
