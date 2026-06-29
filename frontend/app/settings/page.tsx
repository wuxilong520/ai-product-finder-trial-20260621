import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { Card } from "@/design-system/components";
import { t } from "@/lib/i18n";
import { getServerLanguage } from "@/lib/i18n-server";

export default async function SettingsPage() {
  const lang = await getServerLanguage();
  const text = t(lang);

  return (
    <XBorderLayout lang={lang} activePath="admin">
      <Card className="border-white/8 bg-[#121c2c] p-6 shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
        <h1 className="text-3xl font-semibold tracking-tight text-white">{text.settingsPageTitle}</h1>
        <p className="mt-2 text-sm leading-7 text-white/60">{text.settingsPageDesc}</p>
      </Card>
    </XBorderLayout>
  );
}
