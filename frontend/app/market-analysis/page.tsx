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
        <div className="grid gap-4 md:grid-cols-4">
          <div className="rounded-[18px] border border-white/8 bg-[#121c2c] px-5 py-5 shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <div className="text-sm text-white/45">趋势分析</div>
            <div className="mt-2 text-xl font-semibold text-white">实时市场热度</div>
          </div>
          <div className="rounded-[18px] border border-white/8 bg-[#121c2c] px-5 py-5 shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <div className="text-sm text-white/45">类目竞争</div>
            <div className="mt-2 text-xl font-semibold text-white">竞争度评分</div>
          </div>
          <div className="rounded-[18px] border border-white/8 bg-[#121c2c] px-5 py-5 shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <div className="text-sm text-white/45">机会指数</div>
            <div className="mt-2 text-xl font-semibold text-white">利润空间判断</div>
          </div>
          <div className="rounded-[18px] border border-white/8 bg-[#121c2c] px-5 py-5 shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <div className="text-sm text-white/45">分析结果</div>
            <div className="mt-2 text-xl font-semibold text-white">统一卡片展示</div>
          </div>
        </div>
        <MarketAnalysisCard lang={lang} />
      </div>
    </XBorderLayout>
  );
}
