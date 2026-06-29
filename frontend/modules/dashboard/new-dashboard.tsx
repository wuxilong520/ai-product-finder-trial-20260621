import { cookies } from "next/headers";

import { DashboardCommandCenter } from "@/components/dashboard/dashboard-command-center";
import { getCurrentUser, getDashboardSources, getDashboardSummary, getDashboardTasks, getDashboardTrends, getP5Rankings, getP5Recommendations, getProducts } from "@/lib/api";
import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { TOKEN_KEY } from "@/lib/auth";
import { Language } from "@/lib/i18n";

export async function NewDashboard({
  token,
  lang,
}: {
  token: string;
  lang: Language;
}) {
  const [summary, trends, tasks, sources, productList, rankings, recommendations, user] = await Promise.all([
    getDashboardSummary(token),
    getDashboardTrends(token),
    getDashboardTasks(token),
    getDashboardSources(token),
    getProducts("", token),
    getP5Rankings(token).catch(() => null),
    getP5Recommendations({ limit: 10 }, token).catch(() => null),
    getCurrentUser(token).catch(() => null),
  ]);

  return (
    <XBorderLayout lang={lang} activePath="dashboard">
      <DashboardCommandCenter
        lang={lang}
        summary={summary}
        tasks={tasks}
        sources={sources}
        products={productList}
        rankings={rankings}
        recommendations={recommendations}
        isAdmin={Boolean(user?.is_superuser)}
      />
    </XBorderLayout>
  );
}
