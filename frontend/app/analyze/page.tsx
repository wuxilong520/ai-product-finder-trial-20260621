import { AppShell } from "@/components/app-shell";
import { AnalyzePanel } from "@/components/products/analyze-panel";
import { getServerLanguage } from "@/lib/i18n-server";

export default async function AnalyzePage() {
  const lang = await getServerLanguage();

  return (
    <AppShell lang={lang}>
      <AnalyzePanel initialLang={lang} />
    </AppShell>
  );
}
