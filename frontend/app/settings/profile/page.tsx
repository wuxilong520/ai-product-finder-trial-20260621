import { redirect } from "next/navigation";
import { cookies } from "next/headers";
import Link from "next/link";

import { PlanAccessPanel } from "@/components/billing/plan-access-panel";
import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { Card, CardContent, CardHeader, CardTitle, InfoTile, Button } from "@/design-system/components";
import { ApiKeyPanel } from "@/components/settings/api-key-panel";
import { ROUTES } from "@/config/routes";
import { TOKEN_KEY } from "@/lib/auth";
import { isAuthError } from "@/lib/api";
import { getAccountOverview, getApiKeys } from "@/lib/api/account";
import { getServerLanguage } from "@/lib/i18n-server";

export default async function SettingsProfilePage() {
  const token = (await cookies()).get(TOKEN_KEY)?.value || "";
  if (!token) redirect(ROUTES.login);
  const lang = await getServerLanguage();
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
          <div className="text-xs uppercase tracking-[0.24em] text-white/40">商航AI · 账号信息</div>
          <h1 className="text-3xl font-semibold tracking-tight text-white">账号信息</h1>
          <p className="mt-2 text-sm leading-7 text-white/60">
            这里直接展示你的真实账号、工作区、当前套餐、API Key 状态和最近订单，方便你判断当前工作区的使用状态。
          </p>
        </Card>

        <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
          <Card className="border-white/8 bg-[#121c2c]">
            <CardHeader><CardTitle>账号身份</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              <InfoTile label="邮箱" value={overview.user.email} />
              <InfoTile label="名称" value={overview.user.full_name || "未填写"} />
            </CardContent>
          </Card>

          <Card className="border-white/8 bg-[#121c2c]">
            <CardHeader><CardTitle>账号状态</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              <InfoTile label="当前状态" value={overview.user.is_active ? "正常" : "已停用"} />
              <InfoTile label="账号类型" value={overview.user.is_superuser ? "管理员账号" : "普通用户"} />
            </CardContent>
          </Card>

          <Card className="border-white/8 bg-[#121c2c]">
            <CardHeader><CardTitle>当前套餐</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              <InfoTile label="套餐" value={overview.billing.plan_name} />
              <InfoTile label="状态" value={overview.billing.status} />
            </CardContent>
          </Card>

          <Card className="border-white/8 bg-[#121c2c]">
            <CardHeader><CardTitle>最近更新时间</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              <InfoTile label="账号更新" value={overview.user.updated_at.replace("T", " ")} />
              <InfoTile label="套餐更新" value={overview.billing.updated_at.replace("T", " ")} />
            </CardContent>
          </Card>
        </div>

        <div className="grid gap-6 xl:grid-cols-3">
          <Card className="border-white/8 bg-[#121c2c]">
            <CardHeader><CardTitle>工作区信息</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              <InfoTile label="工作区 ID" value={overview.workspace ? `#${overview.workspace.id}` : "未分配"} />
              <InfoTile label="工作区名称" value={overview.workspace?.name || "未找到"} />
              <InfoTile label="所有者 ID" value={overview.workspace ? `#${overview.workspace.owner_id}` : "未找到"} />
            </CardContent>
          </Card>
          <Card className="border-white/8 bg-[#121c2c]">
            <CardHeader><CardTitle>AI 通道权限</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              <InfoTile label="可用模型" value={overview.billing.allowed_ai_models.join(" / ") || "未开放"} />
              <InfoTile label="可用通道" value={overview.billing.allowed_ai_providers.join(" / ") || "未开放"} />
              <InfoTile label="企业专属模型" value={overview.billing.supports_custom_model ? "支持" : "不支持"} />
            </CardContent>
          </Card>
          <Card className="border-white/8 bg-[#121c2c]">
            <CardHeader><CardTitle>API Key 摘要</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              <InfoTile label="总数" value={String(overview.api_key_summary.total_keys)} />
              <InfoTile label="可用数" value={String(overview.api_key_summary.active_keys)} />
              <InfoTile label="最近状态" value={overview.api_key_summary.latest_key_status || "暂无"} />
            </CardContent>
          </Card>
        </div>

        <PlanAccessPanel currentPlan={overview.billing} title="当前账号的 AI 使用权限" />

        <ApiKeyPanel initialItems={apiKeys.items} />

        <Card className="border-white/8 bg-[#121c2c]">
          <CardHeader>
            <CardTitle>最近订单</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {overview.recent_orders.length ? overview.recent_orders.map((item) => (
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
