import { redirect } from "next/navigation";
import { cookies } from "next/headers";
import Link from "next/link";

import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { Card, CardContent, CardHeader, CardTitle, InfoTile, KpiTile, SectionIntro } from "@/design-system/components";
import { PlanAccessPanel } from "@/components/billing/plan-access-panel";
import { PricingOrdersPanel } from "@/components/billing/pricing-orders-panel";
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
        title: "Workspace Settings",
        desc: "Manage your account, team, plan, and security in one clean place.",
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
        desc: "这里统一管理账号、团队、套餐和安全，不展示技术配置。",
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

  const allowedModels = Array.isArray(overview.billing.allowed_ai_models) ? overview.billing.allowed_ai_models : [];
  const allowedProviders = Array.isArray(overview.billing.allowed_ai_providers) ? overview.billing.allowed_ai_providers : [];
  const shopifyReady = overview.store_links.shopify.admin_read_ready;
  const publishReady = overview.store_links.shopify.publish_ready;
  const paymentReady = overview.payment_status.wechat_pay.checkout_ready;
  const hasApiKey = overview.api_key_summary.active_keys > 0;

  const nextSteps = [
    {
      title: shopifyReady ? "继续做商品分析" : "先补店铺读取参数",
      desc: shopifyReady
        ? "你的 Shopify 读取已经打开，可以继续往市场、商品和利润页走。"
        : "当前还没拿到真实店铺读取能力，先去看店铺绑定页。",
      href: shopifyReady ? ROUTES.insights : ROUTES.settingsStoreLinks,
      label: shopifyReady ? "去市场智能页" : "去店铺绑定页",
    },
    {
      title: hasApiKey ? "API Key 已就绪" : "先生成 API Key",
      desc: hasApiKey
        ? "当前工作区已经有可用 Key，需要接外部工具时可以直接用。"
        : "如果你后面要把商航AI接到外部工具或服务，先在这里生成。",
      href: ROUTES.settingsProfile,
      label: hasApiKey ? "去账号信息页" : "去生成 API Key",
    },
    {
      title: paymentReady ? "套餐可继续升级" : "支付通道还没收口",
      desc: paymentReady
        ? "当前支付通道已经能走正式结算入口，可以直接去看套餐。"
        : "当前不假装支付已经完全收口，这里建议先只看套餐信息。",
      href: ROUTES.pricing,
      label: paymentReady ? "去套餐页" : "去看套餐状态",
    },
    {
      title: publishReady ? "可以继续看执行发布" : "发布能力还在继续收口",
      desc: publishReady
        ? "当前执行层已经允许真实发布，可以继续看上架执行页。"
        : "当前不会假装一键上架已经完全可用，先继续看供应链和利润链路。",
      href: publishReady ? ROUTES.actionLaunchQueue : ROUTES.actionSuppliers,
      label: publishReady ? "去执行页" : "去供应链页",
    },
  ];

  return (
    <XBorderLayout lang={lang} activePath="settings">
      <div className="space-y-6">
        <Card className="border-white/8 bg-[#121c2c] p-6 shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <CardContent className="p-0">
            <SectionIntro
              eyebrow="商航AI · 用户中心"
              title={text.title}
              description={text.desc}
              action={<UpgradeEntry label="去充值 / 升级" />}
            />
            <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              <KpiTile label="当前套餐" value={overview.billing.plan_name} hint="先确认你现在能用哪些能力" />
              <KpiTile label="店铺状态" value={overview.store_links.shopify.status_text} hint="看 Shopify 读取和发布现在走到哪一步" />
              <KpiTile label="账号状态" value={overview.user.is_active ? text.active : "已停用"} hint="确认当前账户是否正常可用" />
              <KpiTile label="API Key" value={hasApiKey ? "已就绪" : "未生成"} hint="接外部工具时会用到" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <CardHeader>
            <CardTitle>你现在下一步最该做什么</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            {nextSteps.map((item) => (
              <LinkCard key={item.title} title={item.title} desc={item.desc} href={item.href} label={item.label} />
            ))}
          </CardContent>
        </Card>

        <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <CardHeader>
            <CardTitle>你现在最需要看的 4 件事</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-4">
            <StageTile title="账号和工作区" desc="先确认你现在在哪个工作区里使用这套系统。" />
            <StageTile title="套餐和模型权限" desc="再确认当前套餐到底能用哪些模型和能力。" />
            <StageTile title="店铺绑定状态" desc="再看 Shopify 读取、绑定和发布现在走到哪一步。" />
            <StageTile title="订单和 API Key" desc="最后看充值记录和 API Key 是否已经准备好。" />
          </CardContent>
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
              <InfoTile label="登录邮箱" value={overview.user.email} />
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
              <InfoTile label="可用模型数量" value={String(allowedModels.length)} />
              <InfoTile label="可用通道数量" value={String(allowedProviders.length)} />
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

        <div className="grid gap-6 xl:grid-cols-2">
          <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <CardTitle>当前套餐真正能用什么</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className="text-xs text-white/45">可用模型</div>
                <div className="mt-2 flex flex-wrap gap-2">
                  {allowedModels.length ? allowedModels.map((item) => (
                    <span key={item} className="rounded-full border border-[#4F7CFF]/20 bg-[#4F7CFF]/10 px-3 py-1 text-xs text-[#D8E3FF]">
                      {item}
                    </span>
                  )) : (
                    <span className="text-sm text-white/60">当前还没有开放模型</span>
                  )}
                </div>
              </div>
              <div>
                <div className="text-xs text-white/45">可用通道</div>
                <div className="mt-2 flex flex-wrap gap-2">
                  {allowedProviders.length ? allowedProviders.map((item) => (
                    <span key={item} className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-white/75">
                      {item}
                    </span>
                  )) : (
                    <span className="text-sm text-white/60">当前还没有开放通道</span>
                  )}
                </div>
              </div>
              <div className="rounded-2xl border border-white/8 bg-white/5 p-4 text-sm leading-7 text-white/65">
                {overview.billing.ai_policy_note || "当前套餐会直接决定你能调用哪些模型、能不能接企业专属模型。"}
              </div>
            </CardContent>
          </Card>

          <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <CardTitle>账户当前真实状态</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <InfoTile label="最近登录" value={overview.user.last_login_at ? overview.user.last_login_at.replace("T", " ").slice(0, 19) : "暂无记录"} />
              <InfoTile label="账号创建时间" value={overview.user.created_at.replace("T", " ").slice(0, 19)} />
              <InfoTile label="工作区创建时间" value={overview.workspace?.created_at ? overview.workspace.created_at.replace("T", " ").slice(0, 19) : "未分配"} />
              <InfoTile label="店铺发布状态" value={overview.store_links.shopify.publish_text} />
            </CardContent>
          </Card>
        </div>

        <div className="grid gap-6 xl:grid-cols-3">
          <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <CardTitle>团队</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <InfoTile label="当前角色" value={overview.user.role === "owner" ? "Owner" : overview.user.role === "admin" ? "Admin" : "Member"} />
              <InfoTile label="当前工作区" value={overview.workspace?.name || "未找到工作区"} />
              <InfoTile label="成员管理" value="当前以工作区为单位做权限隔离" />
            </CardContent>
          </Card>

          <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <CardTitle>套餐</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <InfoTile label="当前套餐" value={overview.billing.plan_name} />
              <InfoTile label="可用模型" value={allowedModels.join(" / ") || "未开放"} />
              <InfoTile label="可用通道" value={allowedProviders.join(" / ") || "未开放"} />
            </CardContent>
          </Card>

          <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <CardTitle>安全</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <InfoTile label="登录方式" value="密码 / 验证码 / 刷新令牌" />
              <InfoTile label="失败限制" value="已启用" />
              <InfoTile label="退出登录" value="支持" />
            </CardContent>
          </Card>
        </div>

        <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <CardHeader>
            <CardTitle>账户中心主入口</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            {[
              { title: "账号信息", desc: "看邮箱、工作区、套餐、订单和 API Key。", href: ROUTES.settingsProfile, label: "进入账号信息" },
              { title: "店铺绑定", desc: "看 Shopify 读取、绑定和真实发布现在走到哪一步。", href: ROUTES.settingsStoreLinks, label: "进入店铺绑定" },
              { title: "密码与安全", desc: "看登录、验证码、忘记密码这些安全入口。", href: ROUTES.settingsSecurity, label: "进入安全页" },
              { title: "套餐与充值", desc: "看当前套餐、订单和下一步升级入口。", href: ROUTES.pricing, label: "进入充值页" },
            ].map((item) => (
              <LinkCard key={item.title} title={item.title} desc={item.desc} href={item.href} label={item.label} />
            ))}
          </CardContent>
        </Card>

        <PlanAccessPanel currentPlan={overview.billing} title="你当前账号真正能调用的 AI 模型" />

        <ApiKeyPanel initialItems={apiKeys.items} />

        <PricingOrdersPanel initialOrders={overview.recent_orders} />

        <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <CardHeader>
            <CardTitle>当前账户中心已经收口到哪里</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3 md:grid-cols-2">
            {[
              "账号、套餐、订单这些信息现在已经能在这里真实查看。",
              "工作区、套餐模型权限、API Key 状态现在已经补进账户中心。",
              "店铺绑定页现在已经能真实告诉你 Shopify 读取、绑定和发布分别是什么状态。",
              "真正的平台自动执行能力没有在账户中心假装成已经完全完成。",
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

function StageTile({ title, desc }: { title: string; desc: string }) {
  return (
    <div className="rounded-2xl border border-white/8 bg-white/5 p-4">
      <div className="text-base font-semibold text-white">{title}</div>
      <div className="mt-2 text-sm leading-7 text-white/60">{desc}</div>
    </div>
  );
}
