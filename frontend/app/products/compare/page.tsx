import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { TaskDrivenPageShell } from "@/components/action-center/task-driven-page-shell";
import { Card, CardContent, CardHeader, CardTitle, EmptyState } from "@/design-system/components";
import { ROUTES, taskDetailRoute } from "@/config/routes";
import { TOKEN_KEY } from "@/lib/auth";
import { getServerLanguage } from "@/lib/i18n-server";
import { formatPercent, getTaskSnapshots } from "@/lib/task-page-data";

export default async function ProductComparePage() {
  const token = (await cookies()).get(TOKEN_KEY)?.value || "";
  if (!token) redirect(ROUTES.login);

  const lang = await getServerLanguage();
  const { tasks, fulls } = await getTaskSnapshots(token, 6);
  const currentTaskId = tasks[0]?.task_id;
  const latestSuccess = fulls.find((item) => item.task.status === "success");

  const decision = latestSuccess?.result?.decision_result;

  const compareRows = fulls
    .filter((item) => item.task.status === "success" && item.result?.decision_result)
    .slice(0, 4)
    .map((item) => ({
      taskId: item.task.task_id,
      recommendation: item.result?.decision_result?.recommendation || "—",
      marketFit: item.result?.decision_result?.market_fit_score,
      supplierFit: item.result?.decision_result?.supplier_fit_score,
      profitScore: item.result?.decision_result?.profit_score,
      truthLevel: item.result?.decision_result?.truth_level || "—",
    }));

  return (
    <TaskDrivenPageShell
      lang={lang}
      activePath="products"
      title="商品对比"
      description="这里先用最近任务里已经生成的决策结果做横向对照，帮助你快速比较哪一轮商品判断更值得继续。"
      badge="Product Compare"
      notice="当前是任务级对比，不是假装已经接入了所有真实商品平台。真正多商品实时横向比，要等最后的平台真实接入。"
      currentTaskId={currentTaskId}
      metrics={[
        { label: "最近任务数", value: `${tasks.length} 个` },
        { label: "最近市场匹配", value: formatPercent(decision?.market_fit_score) },
        { label: "最近供应匹配", value: formatPercent(decision?.supplier_fit_score) },
        { label: "最近利润分", value: formatPercent(decision?.profit_score) },
      ]}
      highlights={[
        {
          title: "看最新商品判断",
          description: "进入最新任务详情，能直接看到这轮商品为什么推荐或不推荐。",
          href: currentTaskId ? taskDetailRoute(currentTaskId) : ROUTES.tasks,
          hrefLabel: "查看最新任务",
        },
        {
          title: "继续新增商品判断",
          description: "如果你要比较不同商品、不同市场或不同策略，可以继续发起新任务。",
          href: ROUTES.createTask,
          hrefLabel: "发起新任务",
        },
        {
          title: "查看全部商品资产",
          description: "如果你已经沉淀了一批商品，可以回商品库继续整理。",
          href: ROUTES.products,
          hrefLabel: "进入商品库",
        },
      ]}
    >
      <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
        <CardHeader>
          <CardTitle>最近几次商品判断对照</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {compareRows.length ? (
            compareRows.map((item) => (
              <div key={item.taskId} className="rounded-2xl border border-white/8 bg-white/[0.03] p-4">
                <div className="flex items-center justify-between gap-3">
                  <h3 className="text-base font-semibold text-white">任务 #{item.taskId}</h3>
                  <span className="text-xs text-white/40">{item.truthLevel}</span>
                </div>
                <div className="mt-4 space-y-2 text-sm text-white/65">
                  <div>结论：{item.recommendation}</div>
                  <div>市场匹配：{formatPercent(item.marketFit)}</div>
                  <div>供应匹配：{formatPercent(item.supplierFit)}</div>
                  <div>利润分：{formatPercent(item.profitScore)}</div>
                </div>
              </div>
            ))
          ) : (
            <EmptyState text="现在还没有成功跑完的商品判断任务，所以这里还没有真实对照结果。" />
          )}
        </CardContent>
      </Card>
    </TaskDrivenPageShell>
  );
}
