import { redirect } from "next/navigation";

import { ROUTES } from "@/config/routes";

export default async function P5DashboardPage() {
  redirect(ROUTES.dashboard);
}
