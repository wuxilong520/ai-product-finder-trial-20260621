import { t } from "@/lib/i18n";
import { getServerLanguage } from "@/lib/i18n-server";

export default async function Loading() {
  const lang = await getServerLanguage();
  const text = t(lang);
  return (
    <div className="flex min-h-screen items-center justify-center bg-app-gradient px-6">
      <div className="glass-card-strong app-skeleton min-w-[260px] rounded-2xl px-6 py-4 text-center text-app-text-secondary">
        {text.loadingDashboard}
      </div>
    </div>
  );
}
