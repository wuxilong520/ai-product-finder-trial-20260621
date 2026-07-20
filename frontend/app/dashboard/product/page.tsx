import { redirect } from "next/navigation";
import { cookies } from "next/headers";

import { ROUTES } from "@/config/routes";
import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { Card } from "@/design-system/components";
import { getProductDashboard } from "@/lib/api/task";

export default async function ProductDashboardPage() {
  const cookieStore = await cookies();
  const token = cookieStore.get("shanghang_token")?.value;
  const lang = (cookieStore.get("shanghang_lang")?.value as "zh" | "en") || "zh";
  if (!token) redirect(ROUTES.login);
  const data = await getProductDashboard(token);

  return (
    <XBorderLayout lang={lang} activePath="action">
      <div className="space-y-6">
        <div>
          <div className="text-xs uppercase tracking-[0.24em] text-white/40">商航AI · 产品化总览</div>
          <h1 className="mt-2 text-3xl font-bold text-white">商业上线总览</h1>
          <p className="mt-2 text-sm text-white/55">这里看系统现在到底能不能上线、能不能收费、能不能放量。</p>
        </div>

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
          <Metric title="当前上线模式" value={data.product_mode} />
          <Metric title="产品化分数" value={`${data.commercial_readiness_score}`} />
          <Metric title="执行成功率" value={`${(data.execution_stability_score).toFixed(2)}%`} />
          <Metric title="利润预测准确率" value={`${(data.profit_reliability_score).toFixed(2)}%`} />
          <Metric title="风险等级" value={data.risk_level} />
        </div>

        <div className="grid gap-6 xl:grid-cols-2">
          <Card className="border-white/8 bg-[#111A2E] p-6">
            <div className="text-sm font-medium text-white">上线判断</div>
            <div className="mt-4 space-y-3 text-sm text-white/75">
              <Row label="可上线" value={data.ready_to_launch ? "是" : "否"} />
              <Row label="可收费" value={data.billing_safe ? "是" : "否"} />
              <Row label="可规模化" value={data.scale_ready ? "是" : "否"} />
              <Row label="上线允许" value={data.launch_allowed ? "允许" : "拦截"} />
              <Row label="放量建议" value={data.scale_recommendation} />
            </div>
          </Card>

          <Card className="border-white/8 bg-[#111A2E] p-6">
            <div className="text-sm font-medium text-white">平台接入状态</div>
            <div className="mt-4 space-y-3 text-sm text-white/75">
              {Object.entries(data.platform_integration_status).map(([key, value]) => (
                <Row key={key} label={key} value={String(value)} />
              ))}
            </div>
          </Card>
        </div>

        <Card className="border-white/8 bg-[#111A2E] p-6">
          <div className="text-sm font-medium text-white">上线拦截原因</div>
          <div className="mt-4 space-y-3 text-sm text-white/75">
            {data.blocking_factors.length ? data.blocking_factors.map((item) => (
              <div key={item} className="rounded-2xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-red-200">{item}</div>
            )) : <div className="rounded-2xl border border-green-500/20 bg-green-500/10 px-4 py-3 text-green-200">当前没有上线阻塞项</div>}
          </div>
        </Card>

        <Card className="border-white/8 bg-[#111A2E] p-6">
          <div className="text-sm font-medium text-white">上线检查清单</div>
          <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-3 text-sm text-white/75">
            {Object.entries(data.launch_checklist.checks).map(([key, value]) => (
              <div key={key} className={`rounded-2xl border px-4 py-3 ${value ? "border-green-500/20 bg-green-500/10 text-green-200" : "border-red-500/20 bg-red-500/10 text-red-200"}`}>
                {key}: {value ? "通过" : "未通过"}
              </div>
            ))}
          </div>
        </Card>
      </div>
    </XBorderLayout>
  );
}

function Metric({ title, value }: { title: string; value: string }) {
  return (
    <Card className="border-white/8 bg-[#111A2E] p-5">
      <div className="text-xs text-white/45">{title}</div>
      <div className="mt-2 text-2xl font-semibold text-white break-all">{value}</div>
    </Card>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-start justify-between gap-3">
      <span className="text-white/55">{label}</span>
      <span className="text-right text-white">{value}</span>
    </div>
  );
}
