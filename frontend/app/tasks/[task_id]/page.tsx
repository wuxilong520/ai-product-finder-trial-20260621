import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { TaskDetailPageClient } from "@/components/tasks/task-detail-page-client";
import { ROUTES } from "@/config/routes";
import { TOKEN_KEY } from "@/lib/auth";
import { getServerLanguage } from "@/lib/i18n-server";

export default async function TaskDetailPage({
  params,
}: {
  params: Promise<{ task_id: string }>;
}) {
  const token = (await cookies()).get(TOKEN_KEY)?.value || "";
  if (!token) {
    redirect(ROUTES.login);
  }
  const lang = await getServerLanguage();
  const { task_id } = await params;
  return <TaskDetailPageClient taskId={Number(task_id)} token={token} lang={lang} />;
}
