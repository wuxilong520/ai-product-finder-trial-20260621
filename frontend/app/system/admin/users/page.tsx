import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { AdminUsersTableClient } from "@/components/admin/admin-users-table-client";
import { InternalAdminConsoleLayout } from "@/components/admin/internal-admin-console-layout";
import { ROUTES } from "@/config/routes";
import { getAdminUsers } from "@/lib/api/admin";
import { TOKEN_KEY } from "@/lib/auth";

export default async function AdminUsersPage() {
  const token = (await cookies()).get(TOKEN_KEY)?.value || "";
  if (!token) redirect(ROUTES.login);

  const data = await getAdminUsers({ token });

  return (
    <InternalAdminConsoleLayout currentHref={ROUTES.systemAdminUsers} title="用户管理">
      <AdminUsersTableClient initialItems={data.items} token={token} />
    </InternalAdminConsoleLayout>
  );
}
