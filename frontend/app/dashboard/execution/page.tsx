import { redirect } from "next/navigation";

import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { Card } from "@/design-system/components";
import { ROUTES } from "@/config/routes";
import { getExecutionDashboard } from "@/lib/api/task";
import { cookies } from "next/headers";

export default async function ExecutionDashboardPage() {
  const cookieStore = await cookies();
  const token = cookieStore.get("shanghang_token")?.value;
  const lang = (cookieStore.get("shanghang_lang")?.value as "zh" | "en") || "zh";
  if (!token) redirect(ROUTES.login);
  const data = await getExecutionDashboard(token);

  return (
    <XBorderLayout lang={lang} activePath="action">
      <div className="space-y-6">
        <div>
          <div className="text-xs uppercase tracking-[0.24em] text-white/40">商航AI · 店铺执行总览</div>
          <h1 className="mt-2 text-3xl font-bold text-white">店铺执行结果总览</h1>
          <p className="mt-2 text-sm text-white/55">这里只展示真实执行日志、拦截情况、队列状态和反馈结果。</p>
        </div>

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <Metric title="GMV 估算" value={String(data.growth_metrics.gmv_estimate)} />
          <Metric title="转化率" value={`${(data.growth_metrics.conversion_rate * 100).toFixed(2)}%`} />
          <Metric title="执行成功率" value={`${(data.growth_metrics.execution_success_rate * 100).toFixed(2)}%`} />
          <Metric title="AI建议准确率" value={`${(data.growth_metrics.ai_decision_accuracy * 100).toFixed(2)}%`} />
        </div>

        <Card className="border-white/8 bg-[#111A2E] p-6">
          <div className="text-sm font-medium text-white">风险分布</div>
          <div className="mt-4 space-y-3">
            {Object.entries(data.insight.risk_distribution).map(([key, value]) => (
              <div key={key}>
                <div className="mb-1 flex items-center justify-between text-sm text-white/70">
                  <span>{key}</span>
                  <span>{value}</span>
                </div>
                <div className="h-3 overflow-hidden rounded-full bg-white/10">
                  <div className="h-full rounded-full bg-[#4F7CFF]" style={{ width: `${Math.min(Number(value) * 20, 100)}%` }} />
                </div>
              </div>
            ))}
          </div>
        </Card>

        <div className="grid gap-4 xl:grid-cols-3">
          <SimpleList title="拦截最多的原因" items={data.insight.most_blocked_decisions.map((item) => `${item.reason}（${item.count}）`)} />
          <SimpleList title="成功率最高的商品" items={data.insight.highest_listing_success.map((item) => `${item.keyword}（${(item.success_rate * 100).toFixed(0)}%）`)} />
          <SimpleList title="最赚钱的商品" items={data.insight.most_profitable_items.map((item) => `${item.keyword}（${item.profit_actual}）`)} />
        </div>

        <Card className="border-white/8 bg-[#111A2E] p-6">
          <div className="text-sm font-medium text-white">全部执行记录</div>
          <div className="mt-4 overflow-x-auto">
            <table className="min-w-full text-sm text-white/75">
              <thead>
                <tr className="border-b border-white/10 text-left text-white/45">
                  <th className="px-3 py-3">关键词</th>
                  <th className="px-3 py-3">市场</th>
                  <th className="px-3 py-3">执行等级</th>
                  <th className="px-3 py-3">平台动作</th>
                  <th className="px-3 py-3">执行状态</th>
                  <th className="px-3 py-3">拦截原因</th>
                </tr>
              </thead>
              <tbody>
                {data.records.map((item, index) => (
                  <tr key={`${item.keyword}-${index}`} className="border-b border-white/5">
                    <td className="px-3 py-3">{item.keyword}</td>
                    <td className="px-3 py-3">{item.market}</td>
                    <td className="px-3 py-3">{item.execution_level}</td>
                    <td className="px-3 py-3">{item.platform_action || "—"}</td>
                    <td className="px-3 py-3">{item.platform_execution_status || "—"}</td>
                    <td className="px-3 py-3">{item.blocked_reason || "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
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
      <div className="mt-2 text-2xl font-semibold text-white">{value}</div>
    </Card>
  );
}

function SimpleList({ title, items }: { title: string; items: string[] }) {
  return (
    <Card className="border-white/8 bg-[#111A2E] p-6">
      <div className="text-sm font-medium text-white">{title}</div>
      <div className="mt-4 space-y-3 text-sm text-white/70">
        {items.length ? items.map((item) => <div key={item} className="rounded-2xl border border-white/8 bg-white/5 px-4 py-3">{item}</div>) : <div>当前还没有数据</div>}
      </div>
    </Card>
  );
}
