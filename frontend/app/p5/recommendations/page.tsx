import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { TaskPanel } from "@/components/dashboard/task-panel";
import { P5Recommendations } from "@/components/p5/p5-recommendations";
import { ROUTES } from "@/config/routes";
import { getDashboardSources, getDashboardTasks } from "@/lib/api";
import { TOKEN_KEY } from "@/lib/auth";
import { EMPTY_DASHBOARD_SOURCES, EMPTY_DASHBOARD_TASKS, safeLoad } from "@/lib/dashboard-fallback";
import { getServerLanguage } from "@/lib/i18n-server";

export default async function P5RecommendationsPage() {
  const lang = await getServerLanguage();
  const cookieStore = await cookies();
  const token = cookieStore.get(TOKEN_KEY)?.value || "";
  if (!token) {
    redirect(ROUTES.login);
  }

  const [tasks, sources] = await Promise.all([
    safeLoad(() => getDashboardTasks(token), EMPTY_DASHBOARD_TASKS),
    safeLoad(() => getDashboardSources(token), EMPTY_DASHBOARD_SOURCES),
  ]);

  return (
    <XBorderLayout
      lang={lang}
      activePath="dashboard"
      rightRail={<TaskPanel token={token} initialTasks={tasks} initialSources={sources} lang={lang} />}
    >
      <P5Recommendations lang={lang} />
    </XBorderLayout>
  );
}
