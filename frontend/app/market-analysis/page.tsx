import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { MarketAnalysisCard } from "@/components/market/market-analysis-card";
import { ROUTES } from "@/config/routes";
import { TOKEN_KEY } from "@/lib/auth";
import { t } from "@/lib/i18n";
import { getServerLanguage } from "@/lib/i18n-server";

export default async function MarketAnalysisPage() {
  const lang = await getServerLanguage();
  const text = t(lang);
  const token = (await cookies()).get(TOKEN_KEY)?.value || "";
  if (!token) redirect(ROUTES.login);

  return (
    <XBorderLayout lang={lang} activePath="market">
      <div className="space-y-5">
        <div className="rounded-[28px] border border-white/8 bg-[#121c2c] p-6 shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <h1 className="text-3xl font-semibold tracking-tight text-white">{text.marketPageTitle}</h1>
          <p className="mt-2 text-sm leading-7 text-white/60">{text.marketPageDesc}</p>
        </div>
        <MarketAnalysisCard lang={lang} />
      </div>
    </XBorderLayout>
  );
}
