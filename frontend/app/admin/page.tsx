import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { AdminEntrancePage } from "@/components/admin/admin-entrance-page";
import { ROUTES } from "@/config/routes";
import { TOKEN_KEY } from "@/lib/auth";
import { getCurrentUser, isAuthError } from "@/lib/api-gateway";

export default async function AdminPage() {
  const token = (await cookies()).get(TOKEN_KEY)?.value || "";

  if (!token) {
    return <AdminEntrancePage isLoggedIn={false} hasAdminAccess={false} />;
  }

  try {
    const user = await getCurrentUser(token);
    if (user.is_superuser) {
      redirect(ROUTES.systemAdmin);
    }
    return <AdminEntrancePage isLoggedIn={true} hasAdminAccess={false} />;
  } catch (error) {
    if (isAuthError(error)) {
      return <AdminEntrancePage isLoggedIn={false} hasAdminAccess={false} />;
    }
    throw error;
  }
}
