import { redirect } from "next/navigation";
import { cookies } from "next/headers";
import Link from "next/link";

import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { Card, CardContent, CardHeader, CardTitle, InfoTile, Button } from "@/design-system/components";
import { ROUTES } from "@/config/routes";
import { TOKEN_KEY } from "@/lib/auth";
import { getCurrentUser, isAuthError } from "@/lib/api";
import { getCurrentBillingStatus, getBillingOrders } from "@/lib/api/billing";
import { getServerLanguage } from "@/lib/i18n-server";

export default async function SettingsProfilePage() {
  const token = (await cookies()).get(TOKEN_KEY)?.value || "";
  if (!token) redirect(ROUTES.login);
  const lang = await getServerLanguage();
  let user;
  let billing;
  let orders;
  try {
    [user, billing, orders] = await Promise.all([
      getCurrentUser(token),
      getCurrentBillingStatus(token),
      getBillingOrders(token),
    ]);
  } catch (error) {
    if (isAuthError(error)) {
      redirect(ROUTES.login);
    }
    throw error;
  }

  return (
    <XBorderLayout lang={lang} activePath="settings">
      <div className="space-y-6">
        <Card className="border-white/8 bg-[#121c2c] p-6 shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <h1 className="text-3xl font-semibold tracking-tight text-white">账号信息</h1>
          <p className="mt-2 text-sm leading-7 text-white/60">
            这里现在直接展示你的真实账号、当前套餐和最近订单，不再只是说明页。
          </p>
        </Card>

        <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
          <Card className="border-white/8 bg-[#121c2c]">
            <CardHeader><CardTitle>账号身份</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              <InfoTile label="邮箱" value={user.email} />
              <InfoTile label="名称" value={user.full_name || "未填写"} />
            </CardContent>
          </Card>

          <Card className="border-white/8 bg-[#121c2c]">
            <CardHeader><CardTitle>账号状态</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              <InfoTile label="当前状态" value={user.is_active ? "正常" : "已停用"} />
              <InfoTile label="账号类型" value={user.is_superuser ? "管理员账号" : "普通用户"} />
            </CardContent>
          </Card>

          <Card className="border-white/8 bg-[#121c2c]">
            <CardHeader><CardTitle>当前套餐</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              <InfoTile label="套餐" value={billing.plan_name} />
              <InfoTile label="状态" value={billing.status} />
            </CardContent>
          </Card>

          <Card className="border-white/8 bg-[#121c2c]">
            <CardHeader><CardTitle>最近更新时间</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              <InfoTile label="账号更新" value={user.updated_at.replace("T", " ")} />
              <InfoTile label="套餐更新" value={billing.updated_at.replace("T", " ")} />
            </CardContent>
          </Card>
        </div>

        <Card className="border-white/8 bg-[#121c2c]">
          <CardHeader>
            <CardTitle>最近订单</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {orders.orders.length ? orders.orders.slice(0, 5).map((item) => (
              <div key={item.id} className="rounded-2xl border border-white/8 bg-white/5 p-4 text-sm text-white/75">
                <div className="font-medium text-white">订单 #{item.id}</div>
                <div className="mt-1">套餐：{item.plan_name} · 状态：{item.status}</div>
                <div className="mt-1">金额：{item.currency} {(item.amount_cents / 100).toFixed(2)} · 支付方式：{item.provider_name || "未指定"}</div>
              </div>
            )) : (
              <div className="rounded-2xl border border-white/8 bg-white/5 p-4 text-sm text-white/60">
                你现在还没有订单记录，购买套餐后这里会自动显示。
              </div>
            )}
          </CardContent>
        </Card>

        <div className="flex flex-wrap gap-3">
          <Button asChild><Link href={ROUTES.pricing}>去充值 / 升级</Link></Button>
          <Button asChild variant="secondary"><Link href={ROUTES.settingsSecurity}>去看密码与安全</Link></Button>
        </div>
      </div>
    </XBorderLayout>
  );
}
