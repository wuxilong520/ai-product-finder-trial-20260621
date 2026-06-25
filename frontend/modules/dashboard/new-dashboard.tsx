import { NewDashboardClient } from "@/modules/dashboard/new-dashboard-client";
import { getDashboardSources, getDashboardSummary, getDashboardTasks, getDashboardTrends, getProducts } from "@/lib/api";
import { Language } from "@/lib/i18n";

export async function NewDashboard({
  token,
  lang,
}: {
  token: string;
  lang: Language;
}) {
  const [summary, trends, tasks, sources, productList] = await Promise.all([
    getDashboardSummary(token),
    getDashboardTrends(token),
    getDashboardTasks(token),
    getDashboardSources(token),
    getProducts("", token),
  ]);

  return (
    <NewDashboardClient
      token={token}
      lang={lang}
      initialSummary={summary}
      initialTrends={trends}
      initialTasks={tasks}
      initialSources={sources}
      productList={productList}
    />
  );
}
