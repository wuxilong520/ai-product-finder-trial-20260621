import { redirect } from "next/navigation";

import { ROUTES } from "@/config/routes";

export default async function AIDiscoveryPage() {
  redirect(ROUTES.dashboard);
}
