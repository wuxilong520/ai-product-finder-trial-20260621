import { redirect } from "next/navigation";
import { cookies } from "next/headers";

import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { Card, CardContent, CardHeader, CardTitle, InfoTile } from "@/design-system/components";
import { UpgradeEntry } from "@/components/billing/upgrade-entry";
import { ROUTES } from "@/config/routes";
import { TOKEN_KEY } from "@/lib/auth";
import { getBillingOrders, getCurrentBillingStatus } from "@/lib/api/billing";
import { isAuthError } from "@/lib/api";
import { getServerLanguage } from "@/lib/i18n-server";

export default async function SettingsPage() {
  const lang = await getServerLanguage();
  const token = (await cookies()).get(TOKEN_KEY)?.value || "";
  const text = lang === "en"
    ? {
        title: "Account Settings",
        desc: "Manage store links, account details, and login password here without any technical settings.",
        store: "Store Links",
        storeStatus: "Current Status",
        storeCount: "Store Count",
        manageable: "Manageable",
        pending: "Waiting for access",
        profile: "Profile",
        accountType: "Account Type",
        accountState: "Status",
        formal: "Standard Account",
        active: "Active",
        password: "Password Change",
        security: "Security Status",
        entry: "Update Entry",
        enabled: "Enabled",
        coming: "Coming to this page",
      }
    : {
        title: "账户设置",
        desc: "这里统一管理店铺绑定、账号信息和登录密码，不展示任何技术配置。",
        store: "店铺绑定",
        storeStatus: "当前状态",
        storeCount: "店铺数量",
        manageable: "可管理",
        pending: "待接入展示",
        profile: "账号信息",
        accountType: "账户类型",
        accountState: "使用状态",
        formal: "正式账户",
        active: "正常",
        password: "登录密码修改",
        security: "安全状态",
        entry: "修改入口",
        enabled: "已启用",
        coming: "即将接入当前页",
      };

  if (!token) {
    redirect(ROUTES.login);
  }

  let billing;
  let orders;
  try {
    [billing, orders] = await Promise.all([
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
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <h1 className="text-3xl font-semibold tracking-tight text-white">{text.title}</h1>
              <p className="mt-2 text-sm leading-7 text-white/60">{text.desc}</p>
            </div>
            <UpgradeEntry label="去充值 / 升级" />
          </div>
        </Card>

        <div className="grid gap-6 xl:grid-cols-3">
          <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <CardTitle>当前订阅</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <InfoTile label="套餐状态" value={billing.status} />
              <InfoTile label="当前套餐" value={billing.plan_name} />
              <InfoTile label="最近更新时间" value={billing.updated_at.replace("T", " ")} />
            </CardContent>
          </Card>

          <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <CardTitle>{text.store}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <InfoTile label={text.storeStatus} value={text.manageable} />
              <InfoTile label={text.storeCount} value="接入后显示真实店铺数" />
            </CardContent>
          </Card>

          <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <CardTitle>{text.profile}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <InfoTile label={text.accountType} value={text.formal} />
              <InfoTile label={text.accountState} value={text.active} />
            </CardContent>
          </Card>

          <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <CardTitle>{text.password}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <InfoTile label={text.security} value={text.enabled} />
              <InfoTile label={text.entry} value="使用忘记密码或邮箱验证码登录" />
            </CardContent>
          </Card>
        </div>

        <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <CardHeader>
            <CardTitle>最近订单</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {orders.orders.length ? orders.orders.slice(0, 5).map((item) => (
              <div key={item.id} className="rounded-2xl border border-white/8 bg-white/5 p-4 text-sm text-white/75">
                <div className="font-medium text-white">订单 #{item.id}</div>
                <div className="mt-1">套餐：{item.plan_name} · 状态：{item.status}</div>
                <div className="mt-1">支付方式：{item.provider_name || "未指定"} · 金额：{item.currency} {(item.amount_cents / 100).toFixed(2)}</div>
              </div>
            )) : (
              <div className="rounded-2xl border border-white/8 bg-white/5 p-4 text-sm text-white/60">
                你当前还没有订单记录，后面购买套餐后这里会自动展示。
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </XBorderLayout>
  );
}
