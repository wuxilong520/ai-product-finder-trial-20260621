import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { TaskCard } from "@/components/TaskCard";
import { PlanAccessPanel } from "@/components/billing/plan-access-panel";
import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { Card, Button, StatusAlert } from "@/design-system/components";
import { ROUTES } from "@/config/routes";
import { getCurrentBillingStatus } from "@/lib/api/billing";
import { getTaskList } from "@/lib/api/task";
import { TOKEN_KEY } from "@/lib/auth";
import { getServerLanguage } from "@/lib/i18n-server";
import Link from "next/link";

export default async function TasksPage() {
  const lang = await getServerLanguage();
  const token = (await cookies()).get(TOKEN_KEY)?.value || "";
  if (!token) {
    redirect(ROUTES.login);
  }
  let tasksError: string | null = null;
  const [tasks, currentPlan] = await Promise.all([
    getTaskList(token).catch((error) => {
      tasksError = error instanceof Error ? error.message : "任务列表暂时不可用";
      return [];
    }),
    getCurrentBillingStatus(token).catch(() => null),
  ]);

  return (
    <XBorderLayout lang={lang} activePath="action">
      <div className="space-y-6">
        <Card className="border-white/8 bg-[#111A2E] p-6">
          <div className="flex flex-col gap-5 md:flex-row md:items-end md:justify-between">
            <div>
              <div className="text-xs uppercase tracking-[0.24em] text-white/40">商航AI · AI分析中心</div>
              <h1 className="mt-2 text-3xl font-bold text-white">AI商业判断任务</h1>
              <p className="mt-3 max-w-2xl text-sm leading-7 text-white/55">
                从发现机会、供应方案判断、利润测算到最终建议，所有动作都会沉淀为任务。你重点看结论、风险和下一步，不需要看技术细节。
              </p>
            </div>
            <Button asChild>
              <Link href={ROUTES.createTask}>发起新的商业判断</Link>
            </Button>
          </div>
          <div className="mt-5 grid gap-4 md:grid-cols-3">
            <div className="rounded-2xl border border-white/8 bg-white/5 px-4 py-4 text-sm text-white/75">
              <div className="text-xs text-white/45">任务模式</div>
              <div className="mt-2 text-lg font-semibold text-white">异步分析</div>
            </div>
            <div className="rounded-2xl border border-white/8 bg-white/5 px-4 py-4 text-sm text-white/75">
              <div className="text-xs text-white/45">报告能力</div>
              <div className="mt-2 text-lg font-semibold text-white">结论 + 原因 + 路径</div>
            </div>
            <div className="rounded-2xl border border-white/8 bg-white/5 px-4 py-4 text-sm text-white/75">
              <div className="text-xs text-white/45">当前任务数</div>
              <div className="mt-2 text-lg font-semibold text-white">{tasks.length}</div>
            </div>
          </div>
        </Card>

        <PlanAccessPanel currentPlan={currentPlan} title="当前任务会使用的 AI 权限" compact />

        {tasksError ? <StatusAlert status="warning" message={`任务中心接口暂时失败：${tasksError}`} /> : null}

        {tasks.length ? (
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {tasks.map((task) => (
              <TaskCard key={task.task_id} task={task} />
            ))}
          </div>
        ) : (
          <Card className="border-white/8 bg-[#111A2E] p-8 text-center text-white/60">
            这里还没有 AI 分析任务。你可以先发起一个新的商业判断任务。
          </Card>
        )}
      </div>
    </XBorderLayout>
  );
}
