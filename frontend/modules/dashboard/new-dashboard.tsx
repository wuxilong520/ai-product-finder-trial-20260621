import { redirect } from "next/navigation";

import { DashboardCommandCenter } from "@/components/dashboard/dashboard-command-center";
import { getCurrentUser, getDashboardSources, getDashboardSummary, getDashboardTasks, getDashboardTrends, getP5Rankings, getP5Recommendations, getProducts, isAuthError } from "@/lib/api-gateway";
import { getCurrentBillingStatus } from "@/lib/api/billing";
import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { ROUTES } from "@/config/routes";
import { Language } from "@/lib/i18n";
import { Card, CardContent, StatusAlert } from "@/design-system/components";
import { EMPTY_DASHBOARD_SOURCES, EMPTY_DASHBOARD_SUMMARY, EMPTY_DASHBOARD_TASKS, EMPTY_DASHBOARD_TRENDS, safeLoad } from "@/lib/dashboard-fallback";

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
  let loadError: string | null = null;

  [summary, trends, tasks, sources, productList] = await Promise.all([
    safeLoad(async () => {
      try {
        return await getDashboardSummary(token);
      } catch (error) {
        if (isAuthError(error)) redirect(ROUTES.login);
        throw error;
      }
    }, EMPTY_DASHBOARD_SUMMARY),
    safeLoad(() => getDashboardTrends(token), EMPTY_DASHBOARD_TRENDS),
    safeLoad(() => getDashboardTasks(token), EMPTY_DASHBOARD_TASKS),
    safeLoad(() => getDashboardSources(token), EMPTY_DASHBOARD_SOURCES),
    safeLoad(async () => {
      try {
        return await getProducts("", token);
      } catch (error) {
        if (isAuthError(error)) redirect(ROUTES.login);
        throw error;
      }
    }, { items: [], total: 0 }),
  ]);

  if (!summary.cards.length && !productList.total) {
    loadError = "首页核心数据暂时没拿回来，页面先用保底内容打开。你可以先去市场页、采购方案页或稍后刷新重试。";
  }

  const [rankings, recommendations, user, currentPlan] = await Promise.all([
    getP5Rankings(token).catch(() => null),
    getP5Recommendations({ limit: 10 }, token).catch(() => null),
    getCurrentUser(token).catch((error) => {
      if (isAuthError(error)) {
        return null;
      }
      return null;
    }),
    getCurrentBillingStatus(token).catch(() => null),
  ]);

  return (
    <XBorderLayout lang={lang} activePath="home">
      <div className="space-y-4">
        {loadError ? (
          <Card className="border-white/8 bg-[#121c2c]">
            <CardContent className="p-5">
              <StatusAlert status="warning" message={loadError} />
            </CardContent>
          </Card>
        ) : null}
        <DashboardCommandCenter
          lang={lang}
          summary={summary}
          tasks={tasks}
          sources={sources}
          products={productList}
          rankings={rankings}
          recommendations={recommendations}
          isAdmin={Boolean(user?.is_superuser)}
          currentPlan={currentPlan}
        />
      </div>
    </XBorderLayout>
  );
}
