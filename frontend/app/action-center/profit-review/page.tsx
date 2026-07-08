import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { TaskDrivenPageShell } from "@/components/action-center/task-driven-page-shell";
import { ProfitPublishCenter } from "@/components/action-center/profit-publish-center";
import { Card, CardContent, CardHeader, CardTitle, EmptyState } from "@/design-system/components";
import { ROUTES, taskDetailRoute } from "@/config/routes";
import { TOKEN_KEY } from "@/lib/auth";
import { getServerLanguage } from "@/lib/i18n-server";
import { formatMoney, formatPercent, getTaskSnapshots } from "@/lib/task-page-data";

export default async function ProfitReviewPage() {
  const token = (await cookies()).get(TOKEN_KEY)?.value || "";
  if (!token) redirect(ROUTES.login);

  const lang = await getServerLanguage();
  const keyword = "air fryer";
  const { tasks, fulls } = await getTaskSnapshots(token, 6);
  const latestSuccess = fulls.find((item) => item.task.status === "success");
  const currentTaskId = tasks[0]?.task_id;

  const profit = latestSuccess?.result?.truth_result?.profit;
  const profitMargin = latestSuccess?.result?.truth_result?.profit_margin;
  const confidence = latestSuccess?.result?.decision_result?.confidence_score;
  const risk = latestSuccess?.result?.decision_result?.risk_score;

  const recentSuccesses = fulls
    .filter((item) => item.task.status === "success" && (item.result?.truth_result || item.result?.decision_result))
    .slice(0, 3);

  return (
    <TaskDrivenPageShell
      lang={lang}
      activePath="action"
      title="利润决策 + 上架准备"
      description="这一步就是你最后拍板的地方：先看利润能不能成立，再看风险和执行等级，最后再决定要不要继续做 Shopify 上架准备。"
      badge="Profit & Publish"
      notice="当前这页已经接上真实决策、上架草稿、发布前检查三条接口。当前唯一不能假装完成的地方，是 production_ready 没通过时，真实发布仍会被系统锁住。"
      currentTaskId={currentTaskId}
      metrics={[
        { label: "最近任务数", value: `${tasks.length} 个` },
        { label: "最近利润估算", value: formatMoney(profit) },
        { label: "最近利润率", value: profitMargin !== undefined ? `${Number(profitMargin).toFixed(2)}%` : "—" },
        { label: "最近可信度", value: formatPercent(confidence, "0-1") },
      ]}
      highlights={[
        {
          title: "先做最后拍板",
          description: "直接在这一页完成利润判断、上架草稿和发布前检查。",
          badge: "第 7 页主流程",
        },
        {
          title: "看完整任务结果",
          description: "如果你想追查历史任务里的 explain、trace、结果明细，可以回任务流看。",
          href: currentTaskId ? taskDetailRoute(currentTaskId) : ROUTES.tasks,
          hrefLabel: "进入任务流",
          badge: currentTaskId ? `任务 #${currentTaskId}` : "任务中心",
        },
        {
          title: "看套餐权限",
          description: "如果你要更深的 explain、更多任务额度或更高模型权限，可以直接去套餐页。",
          href: ROUTES.pricing,
          hrefLabel: "查看套餐",
        },
        {
          title: "重新跑一轮判断",
          description: "如果当前结果不够新，可以重新发起任务拿最新利润和决策结果。",
          href: ROUTES.createTask,
          hrefLabel: "发起新任务",
        },
      ]}
    >
      <ProfitPublishCenter initialKeyword={keyword} />

      <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
        <CardHeader>
          <CardTitle>最近几次最后拍板结果</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {recentSuccesses.length ? (
            recentSuccesses.map((item) => {
              const truth = item.result?.truth_result;
              const decision = item.result?.decision_result;
              return (
                <div key={item.task.task_id} className="rounded-2xl border border-white/8 bg-white/[0.03] p-4">
                  <div className="flex items-center justify-between gap-3">
                    <h3 className="text-base font-semibold text-white">任务 #{item.task.task_id}</h3>
                    <span className="text-xs text-white/40">{item.task.status}</span>
                  </div>
                  <div className="mt-4 space-y-2 text-sm text-white/65">
                    <div>利润估算：{formatMoney(truth?.profit)}</div>
                    <div>利润率：{truth?.profit_margin !== undefined ? `${Number(truth.profit_margin).toFixed(2)}%` : "—"}</div>
                    <div>风险分：{formatPercent(decision?.risk_score)}</div>
                    <div>可信度：{formatPercent(decision?.confidence_score, "0-1")}</div>
                    <div>真值等级：{decision?.truth_level || truth?.truth_level || "—"}</div>
                  </div>
                </div>
              );
            })
          ) : (
            <EmptyState text="还没有跑成功的利润判断任务。先发起一个任务，这里才会出现真实利润数据。" />
          )}
        </CardContent>
      </Card>
    </TaskDrivenPageShell>
  );
}
