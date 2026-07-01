import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { TaskDrivenPageShell } from "@/components/action-center/task-driven-page-shell";
import { Card, CardContent, CardHeader, CardTitle, EmptyState } from "@/design-system/components";
import { ROUTES, taskDetailRoute } from "@/config/routes";
import { TOKEN_KEY } from "@/lib/auth";
import { getServerLanguage } from "@/lib/i18n-server";
import { getTaskSnapshots } from "@/lib/task-page-data";

export default async function LaunchQueuePage() {
  const token = (await cookies()).get(TOKEN_KEY)?.value || "";
  if (!token) redirect(ROUTES.login);

  const lang = await getServerLanguage();
  const { tasks } = await getTaskSnapshots(token, 6);
  const currentTaskId = tasks[0]?.task_id;

  const pendingCount = tasks.filter((task) => task.status === "pending" || task.status === "retrying").length;
  const runningCount = tasks.filter((task) => task.status === "running").length;
  const successCount = tasks.filter((task) => task.status === "success").length;
  const failedCount = tasks.filter((task) => task.status === "failed").length;

  return (
    <TaskDrivenPageShell
      lang={lang}
      activePath="action"
      title="上架执行队列"
      description="这页先把你当前真正跑过的任务队列、状态和重试能力展示出来。真实一键上架动作，放在最后接真实平台时补。"
      badge="Launch Queue"
      notice="现在这里展示的是任务执行队列，不是假装已经能一键上架。真正发到 Amazon / Shopify / 1688 店铺，还差最后的平台真实接入。"
      currentTaskId={currentTaskId}
      metrics={[
        { label: "待处理", value: `${pendingCount} 个` },
        { label: "执行中", value: `${runningCount} 个` },
        { label: "已成功", value: `${successCount} 个` },
        { label: "失败待看", value: `${failedCount} 个` },
      ]}
      highlights={[
        {
          title: "看完整任务队列",
          description: "这里能看到当前所有任务的状态、进度和重试次数。",
          href: ROUTES.tasks,
          hrefLabel: "进入任务中心",
        },
        {
          title: "重新发起一轮执行",
          description: "如果你想继续推进新的商品判断或供应链判断，可以直接新建任务。",
          href: ROUTES.createTask,
          hrefLabel: "发起任务",
        },
        {
          title: "准备接真实店铺",
          description: "等最后接真实平台时，这页会承接真正的执行回传。",
          href: ROUTES.settingsStoreLinks,
          hrefLabel: "店铺绑定准备",
        },
      ]}
    >
      <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
        <CardHeader>
          <CardTitle>最近队列状态</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {tasks.length ? (
            tasks.slice(0, 6).map((task) => (
              <div key={task.task_id} className="rounded-2xl border border-white/8 bg-white/[0.03] p-4">
                <div className="flex items-center justify-between gap-3">
                  <h3 className="text-base font-semibold text-white">任务 #{task.task_id}</h3>
                  <span className="text-xs text-white/40">{task.status}</span>
                </div>
                <div className="mt-4 space-y-2 text-sm text-white/65">
                  <div>进度：{task.progress ?? 0}%</div>
                  <div>重试次数：{task.retry_count ?? 0}</div>
                  <div>最近更新时间：{task.updated_at || "—"}</div>
                </div>
                <a href={taskDetailRoute(task.task_id)} className="mt-4 inline-block text-sm text-cyan-300 hover:text-cyan-200">
                  去看这个任务 →
                </a>
              </div>
            ))
          ) : (
            <EmptyState text="当前还没有任务队列记录。先发起任务，这里才会出现真实执行状态。" />
          )}
        </CardContent>
      </Card>
    </TaskDrivenPageShell>
  );
}
