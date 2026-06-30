import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { TaskCard } from "@/components/TaskCard";
import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { Card, Button } from "@/design-system/components";
import { ROUTES } from "@/config/routes";
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
  const tasks = await getTaskList(token);

  return (
    <XBorderLayout lang={lang} activePath="action">
      <div className="space-y-6">
        <Card className="border-white/8 bg-[#111A2E] p-6">
          <div className="flex flex-col gap-5 md:flex-row md:items-end md:justify-between">
            <div>
              <div className="text-xs uppercase tracking-[0.24em] text-white/40">Action Center</div>
              <h1 className="mt-2 text-3xl font-bold text-white">商业执行任务中心</h1>
              <p className="mt-3 max-w-2xl text-sm leading-7 text-white/55">
                从“发现机会”到“形成建议”，所有动作都会进入任务流，并保留解释、追踪和重试能力。
              </p>
            </div>
            <Button asChild>
              <Link href={ROUTES.createTask}>发起新的商业判断</Link>
            </Button>
          </div>
        </Card>

        {tasks.length ? (
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {tasks.map((task) => (
              <TaskCard key={task.task_id} task={task} />
            ))}
          </div>
        ) : (
          <Card className="border-white/8 bg-[#111A2E] p-8 text-center text-white/60">
            这里还没有任务。你可以先发起一个新的商业判断任务。
          </Card>
        )}
      </div>
    </XBorderLayout>
  );
}
