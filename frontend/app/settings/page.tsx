import { redirect } from "next/navigation";
import { cookies } from "next/headers";
import Link from "next/link";

import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { Card, CardContent, CardHeader, CardTitle, InfoTile } from "@/design-system/components";
import { PlanAccessPanel } from "@/components/billing/plan-access-panel";
import { UpgradeEntry } from "@/components/billing/upgrade-entry";
import { ApiKeyPanel } from "@/components/settings/api-key-panel";
import { ROUTES } from "@/config/routes";
import { TOKEN_KEY } from "@/lib/auth";
import { getAccountOverview, getApiKeys } from "@/lib/api/account";
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

  let overview;
  let apiKeys;
  try {
    [overview, apiKeys] = await Promise.all([
      getAccountOverview(token),
      getApiKeys(token),
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
              <div className="text-xs uppercase tracking-[0.24em] text-white/40">商航AI · 账户中心</div>
              <h1 className="text-3xl font-semibold tracking-tight text-white">{text.title}</h1>
              <p className="mt-2 text-sm leading-7 text-white/60">{text.desc}</p>
            </div>
            <UpgradeEntry label="去充值 / 升级" />
          </div>
        </Card>

        <div className="grid gap-6 xl:grid-cols-4">
          <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <CardTitle>当前订阅</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <InfoTile label="套餐状态" value={overview.billing.status} />
              <InfoTile label="当前套餐" value={overview.billing.plan_name} />
              <InfoTile label="支付通道状态" value={overview.payment_status.wechat_pay.status_text} />
            </CardContent>
          </Card>

          <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <CardTitle>{text.store}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <InfoTile label={text.storeStatus} value={overview.store_links.shopify.status_text} />
              <InfoTile label={text.storeCount} value={overview.store_links.shopify.publish_text} />
            </CardContent>
          </Card>

          <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <CardTitle>{text.profile}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <InfoTile label={text.accountType} value={overview.user.is_superuser ? "管理员账号" : text.formal} />
              <InfoTile label={text.accountState} value={overview.user.is_active ? text.active : "已停用"} />
            </CardContent>
          </Card>

          <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <CardTitle>{text.password}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <InfoTile label={text.security} value={text.enabled} />
              <InfoTile label={text.entry} value="密码登录、邮箱验证码登录、忘记密码都可用" />
            </CardContent>
          </Card>
        </div>

        <div className="grid gap-6 xl:grid-cols-3">
          <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <CardTitle>当前工作区</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <InfoTile label="工作区 ID" value={overview.workspace ? `#${overview.workspace.id}` : "未分配"} />
              <InfoTile label="工作区名称" value={overview.workspace?.name || "未找到工作区"} />
              <InfoTile label="工作区所有者" value={overview.workspace ? `用户 #${overview.workspace.owner_id}` : "未找到"} />
            </CardContent>
          </Card>

          <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <CardTitle>AI 模型权限</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <InfoTile label="可用模型数量" value={String(overview.billing.allowed_ai_models.length)} />
              <InfoTile label="可用通道数量" value={String(overview.billing.allowed_ai_providers.length)} />
              <InfoTile label="自定义模型" value={overview.billing.supports_custom_model ? "当前套餐支持" : "当前套餐不支持"} />
            </CardContent>
          </Card>

          <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <CardTitle>API Key 状态</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <InfoTile label="总 Key 数" value={String(overview.api_key_summary.total_keys)} />
              <InfoTile label="可用 Key 数" value={String(overview.api_key_summary.active_keys)} />
              <InfoTile label="最近生成状态" value={overview.api_key_summary.latest_key_status || "暂无"} />
            </CardContent>
          </Card>
        </div>

        <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <CardHeader>
            <CardTitle>账户中心主入口</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            {[
              { title: "账号信息", desc: "看邮箱、套餐、最近订单。", href: ROUTES.settingsProfile, label: "进入账号信息" },
              { title: "店铺绑定", desc: "看 Shopify 等平台接入准备状态。", href: ROUTES.settingsStoreLinks, label: "进入店铺绑定" },
              { title: "密码与安全", desc: "走登录、验证码和找回密码入口。", href: ROUTES.settingsSecurity, label: "进入安全页" },
              { title: "套餐与充值", desc: "去看升级、订单、当前权限。", href: ROUTES.pricing, label: "进入充值页" },
            ].map((item) => (
              <LinkCard key={item.title} title={item.title} desc={item.desc} href={item.href} label={item.label} />
            ))}
          </CardContent>
        </Card>

        <PlanAccessPanel currentPlan={overview.billing} title="你当前账号真正能调用的 AI 模型" />

        <ApiKeyPanel initialItems={apiKeys.items} />

        <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <CardHeader>
            <CardTitle>最近订单</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {overview.recent_orders.length ? overview.recent_orders.map((item) => (
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

        <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <CardHeader>
            <CardTitle>当前账户页说真话</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3 md:grid-cols-2">
            {[
              "账号、套餐、订单这些信息现在已经能在这里真实查看。",
              "工作区、套餐模型权限、API Key 状态现在已经补进账户中心。",
              "用户自助店铺绑定页已经有入口，但还没收口成真正可绑定成功的最终状态。",
              "真正的平台自动执行能力没有在账户页假装成已经完成。",
            ].map((item) => (
              <div key={item} className="rounded-2xl border border-white/8 bg-white/5 p-4 text-sm leading-7 text-white/70">
                {item}
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </XBorderLayout>
  );
}

function LinkCard({
  title,
  desc,
  href,
  label,
}: {
  title: string;
  desc: string;
  href: string;
  label: string;
}) {
  return (
    <Link
      href={href}
      className="rounded-2xl border border-white/8 bg-white/5 p-4 transition hover:border-[#4F7CFF]/30 hover:bg-[#4F7CFF]/10"
    >
      <div className="text-base font-semibold text-white">{title}</div>
      <div className="mt-2 text-sm leading-7 text-white/60">{desc}</div>
      <div className="mt-4 text-sm font-medium text-[#9CC0FF]">{label}</div>
    </Link>
  );
}
