import { redirect } from "next/navigation";

import { DashboardCommandCenter } from "@/components/dashboard/dashboard-command-center";
import { getCurrentUser, getDashboardSources, getDashboardSummary, getDashboardTasks, getDashboardTrends, getP5Rankings, getP5Recommendations, getProducts, isAuthError } from "@/lib/api-gateway";
import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { ROUTES } from "@/config/routes";
import { Language } from "@/lib/i18n";

export async function NewDashboard({
  token,
  lang,
}: {
  token: string;
  lang: Language;
}) {
  let summary;
  let trends;
  let tasks;
  let sources;
  let productList;

  try {
    [summary, trends, tasks, sources, productList] = await Promise.all([
      getDashboardSummary(token),
      getDashboardTrends(token),
      getDashboardTasks(token),
      getDashboardSources(token),
      getProducts("", token),
    ]);
  } catch (error) {
    if (isAuthError(error)) {
      redirect(ROUTES.login);
    }
    throw error;
  }

  const [rankings, recommendations, user] = await Promise.all([
    getP5Rankings(token).catch(() => null),
    getP5Recommendations({ limit: 10 }, token).catch(() => null),
    getCurrentUser(token).catch((error) => {
      if (isAuthError(error)) {
        return null;
      }
      return null;
    }),
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
