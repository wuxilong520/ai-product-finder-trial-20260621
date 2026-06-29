import { redirect } from "next/navigation";

import { ROUTES } from "@/config/routes";

export default async function P5RecommendationsPage() {
  redirect(ROUTES.dashboard);
}
