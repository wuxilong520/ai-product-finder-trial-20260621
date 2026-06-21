import { AppShell } from "@/components/app-shell";
import { AnalyzePanel } from "@/components/products/analyze-panel";
import { SystemStatusPanel } from "@/components/system/system-status-panel";
import { getServerLanguage } from "@/lib/i18n-server";

export default async function AnalyzePage() {
  const lang = await getServerLanguage();

  return (
    <AppShell lang={lang}>
      <div className="mb-6">
        <SystemStatusPanel lang={lang} />
      </div>
      <AnalyzePanel initialLang={lang} />
    </AppShell>
  );
}
