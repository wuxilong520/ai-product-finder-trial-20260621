import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { TaskDrivenPageShell } from "@/components/action-center/task-driven-page-shell";
import { Card, CardContent, CardHeader, CardTitle, EmptyState } from "@/design-system/components";
import { ROUTES, taskDetailRoute } from "@/config/routes";
import { TOKEN_KEY } from "@/lib/auth";
import { getServerLanguage } from "@/lib/i18n-server";
import { formatMoney, getTaskSnapshots } from "@/lib/task-page-data";

export default async function PriceComparePage() {
  const token = (await cookies()).get(TOKEN_KEY)?.value || "";
  if (!token) redirect(ROUTES.login);

  const lang = await getServerLanguage();
  const { tasks, fulls } = await getTaskSnapshots(token, 6);
  const currentTaskId = tasks[0]?.task_id;
  const latestSuccess = fulls.find((item) => item.task.status === "success");

  const sellingPrice = latestSuccess?.result?.truth_result?.selling_price;
  const marketPrice = latestSuccess?.result?.truth_result?.real_market_price;
  const supplierCost = latestSuccess?.result?.truth_result?.supplier_cost;
  const totalCost = latestSuccess?.result?.truth_result?.total_cost;

  const compareRows = fulls
    .filter((item) => item.task.status === "success")
    .slice(0, 3)
    .map((item) => ({
      taskId: item.task.task_id,
      sellingPrice: item.result?.truth_result?.selling_price,
      marketPrice: item.result?.truth_result?.real_market_price,
      supplierCost: item.result?.truth_result?.supplier_cost,
      totalCost: item.result?.truth_result?.total_cost,
    }));

  return (
    <TaskDrivenPageShell
      lang={lang}
      activePath="action"
      title="价格对比"
      description="价格对比先基于你已经跑过的任务结果，把售价、市场价、供应成本和总成本摆出来。真正跨平台的实时比价，留到最后接真实平台。"
      badge="Price Compare"
      notice="当前页面展示的是任务结果里已经沉淀下来的价格数据，不是假装已经拿到了 Amazon / 1688 / Shopify 的实时公开全量价格。"
      currentTaskId={currentTaskId}
      metrics={[
        { label: "最近售价", value: formatMoney(sellingPrice) },
        { label: "最近市场价", value: formatMoney(marketPrice) },
        { label: "最近供应成本", value: formatMoney(supplierCost) },
        { label: "最近总成本", value: formatMoney(totalCost) },
      ]}
      highlights={[
        {
          title: "看完整成本拆解",
          description: "直接去最新任务详情页，看 explain 里的成本拆分。",
          href: currentTaskId ? taskDetailRoute(currentTaskId) : ROUTES.tasks,
          hrefLabel: "查看任务详情",
        },
        {
          title: "重新发起价格判断",
          description: "你可以换关键词、市场类型或成本模式，重新跑一轮。",
          href: ROUTES.createTask,
          hrefLabel: "发起新任务",
        },
        {
          title: "跨平台实时比价还没接",
          description: "这一步以后接真实平台源时会补成真正的比价页。",
          href: ROUTES.settingsStoreLinks,
          hrefLabel: "查看接入准备",
        },
      ]}
    >
      <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
        <CardHeader>
          <CardTitle>最近几次价格快照</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {compareRows.length ? (
            compareRows.map((item) => (
              <div key={item.taskId} className="rounded-2xl border border-white/8 bg-white/[0.03] p-4">
                <div className="flex items-center justify-between gap-3">
                  <h3 className="text-base font-semibold text-white">任务 #{item.taskId}</h3>
                  <span className="text-xs text-white/40">已完成</span>
                </div>
                <div className="mt-4 space-y-2 text-sm text-white/65">
                  <div>售价：{formatMoney(item.sellingPrice)}</div>
                  <div>市场价：{formatMoney(item.marketPrice)}</div>
                  <div>供应成本：{formatMoney(item.supplierCost)}</div>
                  <div>总成本：{formatMoney(item.totalCost)}</div>
                </div>
              </div>
            ))
          ) : (
            <EmptyState text="当前还没有可展示的价格结果。先跑成功一个任务，这里才会出现真实价格快照。" />
          )}
        </CardContent>
      </Card>
    </TaskDrivenPageShell>
  );
}
