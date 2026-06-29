import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { Card, InfoTile } from "@/design-system/components";
import { ROUTES } from "@/config/routes";
import { getCurrentUser, getDashboardSources, getDashboardTasks, getSystemHealth } from "@/lib/api-gateway";
import { TOKEN_KEY } from "@/lib/auth";
import { t } from "@/lib/i18n";
import { getServerLanguage } from "@/lib/i18n-server";

export default async function SystemAdminPage() {
  const lang = await getServerLanguage();
  const text = t(lang);
  const token = (await cookies()).get(TOKEN_KEY)?.value || "";
  if (!token) redirect(ROUTES.login);

  const user = await getCurrentUser(token);
  if (!user.is_superuser) redirect(ROUTES.dashboard);

  const [health, tasks, sources] = await Promise.all([
    getSystemHealth(),
    getDashboardTasks(token),
    getDashboardSources(token),
  ]);

  return (
    <XBorderLayout lang={lang} activePath="admin">
      <div className="space-y-5">
        <Card className="border-white/8 bg-[#121c2c] p-6 shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <h1 className="text-3xl font-semibold tracking-tight text-white">{text.adminPageTitle}</h1>
          <p className="mt-2 text-sm leading-7 text-white/60">{text.adminPageDesc}</p>
        </Card>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <InfoTile label={text.adminSystemStatus} value={health.status} />
          <InfoTile label={text.adminTaskCount} value={String(tasks.recent_runs.length)} />
          <InfoTile label={text.adminSourceCount} value={String(sources.sources.length)} />
          <InfoTile label={text.adminUser} value={user.email} />
        </div>
      </div>
    </XBorderLayout>
  );
}
