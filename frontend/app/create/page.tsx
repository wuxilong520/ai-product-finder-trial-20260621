import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { CreateTaskPageClient } from "@/components/tasks/create-task-page-client";
import { ROUTES } from "@/config/routes";
import { getCurrentBillingStatus } from "@/lib/api/billing";
import { TOKEN_KEY } from "@/lib/auth";
import { getServerLanguage } from "@/lib/i18n-server";

export default async function CreateTaskPage({
  searchParams,
}: {
  searchParams?: Promise<{ category?: string; keyword?: string }>;
}) {
  const token = (await cookies()).get(TOKEN_KEY)?.value || "";
  if (!token) {
    redirect(ROUTES.login);
  }
  const lang = await getServerLanguage();
  const currentPlan = await getCurrentBillingStatus(token).catch(() => null);
  const resolvedSearchParams = searchParams ? await searchParams : undefined;
  const initialCategory = resolvedSearchParams?.category ? decodeURIComponent(String(resolvedSearchParams.category)) : "";
  const initialKeyword = resolvedSearchParams?.keyword ? decodeURIComponent(String(resolvedSearchParams.keyword)) : "";
  return (
    <CreateTaskPageClient
      token={token}
      lang={lang}
      currentPlan={currentPlan}
      initialCategory={initialCategory}
      initialKeyword={initialKeyword}
    />
  );
}
