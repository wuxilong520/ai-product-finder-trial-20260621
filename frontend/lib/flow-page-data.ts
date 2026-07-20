import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { ROUTES } from "@/config/routes";
import { getDashboardSources, getDashboardTasks, getProducts, isAuthError } from "@/lib/api-gateway";
import { TOKEN_KEY } from "@/lib/auth";
import { EMPTY_DASHBOARD_SOURCES, EMPTY_DASHBOARD_TASKS, safeLoad } from "@/lib/dashboard-fallback";
import { getServerLanguage } from "@/lib/i18n-server";

export async function loadFlowPageData() {
  const lang = await getServerLanguage();
  const cookieStore = await cookies();
  const token = cookieStore.get(TOKEN_KEY)?.value || "";
  if (!token) {
    redirect(ROUTES.login);
  }

  let productsError: string | null = null;
  const products = await safeLoad(
    async () => {
      try {
        return await getProducts("", token);
      } catch (error) {
        if (isAuthError(error)) {
          redirect(ROUTES.login);
        }
        throw error;
      }
    },
    { items: [], total: 0 }
  ).catch((error) => {
    productsError = error instanceof Error ? error.message : "商品数据暂时不可用";
    return { items: [], total: 0 };
  });

  const [tasks, sources] = await Promise.all([
    safeLoad(() => getDashboardTasks(token), EMPTY_DASHBOARD_TASKS),
    safeLoad(() => getDashboardSources(token), EMPTY_DASHBOARD_SOURCES),
  ]);

  return {
    lang,
    token,
    products,
    tasks,
    sources,
    productsError,
  };
}
