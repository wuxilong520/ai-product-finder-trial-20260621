import { redirect } from "next/navigation";
import { cookies } from "next/headers";

import { TaskPanel } from "@/components/dashboard/task-panel";
import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { ProductDetail } from "@/components/products/product-detail";
import { ROUTES } from "@/config/routes";
import { getDashboardSources, getDashboardTasks, getProduct, isAuthError } from "@/lib/api";
import { TOKEN_KEY } from "@/lib/auth";
import { EMPTY_DASHBOARD_SOURCES, EMPTY_DASHBOARD_TASKS, safeLoad } from "@/lib/dashboard-fallback";
import { getServerLanguage } from "@/lib/i18n-server";

export default async function ProductDetailPage({ params }: { params: Promise<{ id: string }> }) {
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

  const resolvedParams = await params;
  let product;
  try {
    product = await getProduct(resolvedParams.id, token);
  } catch (error) {
    if (isAuthError(error)) {
      redirect(ROUTES.login);
    }
    throw error;
  }
  return (
    <XBorderLayout
      lang={lang}
      activePath="products"
      rightRail={<TaskPanel token={token} initialTasks={tasks} initialSources={sources} lang={lang} />}
    >
      <div className="space-y-6">
        <ProductDetail product={product} analysisReport={null} lang={lang} />
      </div>
    </XBorderLayout>
  );
}
