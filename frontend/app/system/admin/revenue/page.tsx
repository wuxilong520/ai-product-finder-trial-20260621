import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { InternalAdminConsoleLayout } from "@/components/admin/internal-admin-console-layout";
import { AdminRevenueTableClient } from "@/components/admin/admin-revenue-table-client";
import { ROUTES } from "@/config/routes";
import { getAdminRevenue } from "@/lib/api/admin";
import { TOKEN_KEY } from "@/lib/auth";

export default async function AdminRevenuePage() {
  const token = (await cookies()).get(TOKEN_KEY)?.value || "";
  if (!token) redirect(ROUTES.login);

  const data = await getAdminRevenue({ token });

  return (
    <InternalAdminConsoleLayout currentHref={ROUTES.systemAdminRevenue} title="收入管理">
      <AdminRevenueTableClient initialData={data} />
    </InternalAdminConsoleLayout>
  );
}
