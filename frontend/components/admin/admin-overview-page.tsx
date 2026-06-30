import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/design-system/components";
import { ROUTES } from "@/config/routes";
import { TOKEN_KEY } from "@/lib/auth";
import { getAdminOverview } from "@/lib/api/admin";
import { getServerLanguage } from "@/lib/i18n-server";

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <Card className="border-white/8 bg-[#121c2c]">
      <CardContent className="p-5">
        <div className="text-sm text-white/50">{label}</div>
        <div className="mt-3 text-3xl font-semibold text-white">{value}</div>
      </CardContent>
    </Card>
  );
}

export async function AdminOverviewPage({ entranceLabel }: { entranceLabel: string }) {
  const lang = await getServerLanguage();
  const token = (await cookies()).get(TOKEN_KEY)?.value || "";
  if (!token) {
    redirect(ROUTES.login);
  }

  const data = await getAdminOverview(token);

  return (
    <XBorderLayout lang={lang} activePath="settings">
      <div className="space-y-6">
        <Card className="border-white/8 bg-[#121c2c] p-6">
          <h1 className="text-3xl font-semibold text-white">运营后台总览</h1>
          <p className="mt-2 text-sm leading-7 text-white/60">
            这里给你看真实用户、工作区、套餐和任务状态，方便你上线后自己运营，不给普通用户展示。
          </p>
          <div className="mt-4 rounded-2xl border border-white/8 bg-white/5 px-4 py-3 text-sm text-white/70">
            当前入口：{entranceLabel}。这套后台已经能看到真实用户、真实工作区、真实任务、真实订单和真实套餐状态。
          </div>
          <div className="mt-3 rounded-2xl border border-[#4F7CFF]/20 bg-[#4F7CFF]/10 px-4 py-3 text-sm text-[#D8E3FF]">
            正式上线后，建议把后台独立到单独网址，比如 `admin.你的域名`，普通用户只访问主站，后台只给你自己和管理员使用。
          </div>
        </Card>

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <StatCard label="用户总数" value={data.summary.total_users} />
          <StatCard label="工作区总数" value={data.summary.total_workspaces} />
          <StatCard label="任务总数" value={data.summary.total_tasks} />
          <StatCard label="付费工作区" value={data.summary.paid_workspaces} />
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          <StatCard label="免费工作区" value={data.summary.free_workspaces} />
          <StatCard label="运行中任务" value={data.summary.running_tasks} />
          <StatCard label="失败任务" value={data.summary.failed_tasks} />
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          <StatCard label="订单总数" value={data.summary.total_orders} />
          <StatCard label="已支付订单" value={data.summary.paid_orders} />
          <StatCard label="累计收入" value={`¥ ${(data.summary.revenue_cents / 100).toFixed(2)}`} />
        </div>

        <div className="grid gap-6 xl:grid-cols-2">
          <Card className="border-white/8 bg-[#121c2c]">
            <CardHeader>
              <CardTitle>最新用户</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {data.recent_users.map((item) => (
                <div key={item.id} className="rounded-2xl border border-white/8 bg-white/5 p-4 text-sm text-white/75">
                  <div className="font-medium text-white">{item.email}</div>
                  <div className="mt-1">角色：{item.role} · 工作区：{item.workspace_id ?? "未绑定"}</div>
                  <div className="mt-1 text-white/45">创建时间：{item.created_at}</div>
                </div>
              ))}
            </CardContent>
          </Card>

          <Card className="border-white/8 bg-[#121c2c]">
            <CardHeader>
              <CardTitle>最新任务</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {data.recent_tasks.map((item) => (
                <div key={item.id} className="rounded-2xl border border-white/8 bg-white/5 p-4 text-sm text-white/75">
                  <div className="font-medium text-white">任务 #{item.id}</div>
                  <div className="mt-1">类型：{item.job_type} · 状态：{item.status}</div>
                  <div className="mt-1">重试：{item.retry_count} 次</div>
                  {item.last_error ? <div className="mt-1 text-[#FFD2D2]">失败原因：{item.last_error}</div> : null}
                </div>
              ))}
            </CardContent>
          </Card>
        </div>

        <div className="grid gap-6 xl:grid-cols-2">
          <Card className="border-white/8 bg-[#121c2c]">
            <CardHeader>
              <CardTitle>套餐状态</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {data.subscription_snapshots.map((item) => (
                <div key={`${item.workspace_id}-${item.updated_at}`} className="rounded-2xl border border-white/8 bg-white/5 p-4 text-sm text-white/75">
                  <div className="font-medium text-white">工作区 #{item.workspace_id}</div>
                  <div className="mt-1">套餐：{item.plan_name}</div>
                  <div className="mt-1">状态：{item.status}</div>
                </div>
              ))}
            </CardContent>
          </Card>

          <Card className="border-white/8 bg-[#121c2c]">
            <CardHeader>
              <CardTitle>配额使用</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {data.quota_snapshots.map((item) => (
                <div key={`${item.workspace_id}-${item.updated_at}`} className="rounded-2xl border border-white/8 bg-white/5 p-4 text-sm text-white/75">
                  <div className="font-medium text-white">工作区 #{item.workspace_id}</div>
                  <div className="mt-1">任务：{item.used_task} / {item.daily_task_limit}</div>
                  <div className="mt-1">接口：{item.used_api} / {item.daily_api_limit}</div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>

        <Card className="border-white/8 bg-[#121c2c]">
          <CardHeader>
            <CardTitle>最近订单</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {data.recent_orders.length ? data.recent_orders.map((item) => (
              <div key={item.id} className="rounded-2xl border border-white/8 bg-white/5 p-4 text-sm text-white/75">
                <div className="font-medium text-white">订单 #{item.id}</div>
                <div className="mt-1">套餐：{item.plan_name} · 状态：{item.status}</div>
                <div className="mt-1">金额：{item.currency} {(item.amount_cents / 100).toFixed(2)}</div>
                <div className="mt-1">支付方式：{item.provider_name || "未指定"}</div>
              </div>
            )) : (
              <div className="rounded-2xl border border-white/8 bg-white/5 p-4 text-sm text-white/60">
                现在还没有真实支付订单，后面接入支付后这里会自动显示。
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </XBorderLayout>
  );
}
