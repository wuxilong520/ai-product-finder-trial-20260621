import { t } from "@/lib/i18n";

export default function Loading() {
  const text = t("zh");
  return (
    <div className="flex min-h-screen items-center justify-center bg-app-gradient px-6">
      <div className="glass-card-strong app-skeleton min-w-[260px] rounded-2xl px-6 py-4 text-center text-app-text-secondary">
        {text.loadingDashboard}
      </div>
    </div>
  );
}
