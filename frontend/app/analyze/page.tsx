import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { AnalyzePanel } from "@/components/products/analyze-panel";
import { MarketAnalysisCard } from "@/components/market/market-analysis-card";
import { Badge, Card } from "@/design-system/components";
import { ROUTES } from "@/config/routes";
import { getProduct, isAuthError } from "@/lib/api";
import { TOKEN_KEY } from "@/lib/auth";
import { getServerLanguage } from "@/lib/i18n-server";
import { t } from "@/lib/i18n";
import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { Brain, Sparkles } from "lucide-react";

export default async function AnalyzePage({
  searchParams,
}: {
  searchParams?: Promise<{ productId?: string }>;
}) {
  const lang = await getServerLanguage();
  const text = t(lang);
  const cookieStore = await cookies();
  const token = cookieStore.get(TOKEN_KEY)?.value || "";
  if (!token) {
    redirect(ROUTES.login);
  }
  const resolvedSearchParams = searchParams ? await searchParams : undefined;
  const productId = resolvedSearchParams?.productId;
  let initialUrl: string | undefined;

  if (productId) {
    try {
      const product = await getProduct(productId, token);
      initialUrl = product.source_url;
    } catch (error) {
      if (isAuthError(error)) {
        redirect(ROUTES.login);
      }
    }
  }

  return (
    <XBorderLayout lang={lang} activePath="analyze">
      <div className="space-y-5">
        <Card className="border-white/8 bg-[linear-gradient(180deg,rgba(255,255,255,0.04),rgba(255,255,255,0.02))] p-5 shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <div className="flex flex-wrap items-center gap-3">
            <Badge variant="brand" className="px-4 py-2 text-sm font-medium">
              <Brain className="h-4 w-4" />
              {text.analyzeBadge}
            </Badge>
            <Badge variant="neutral" className="px-4 py-2 text-sm text-app-text-secondary">
              <Sparkles className="h-4 w-4 text-app-brand-secondary" />
              {text.dashboardQuickEntryAnalyzeTitle}
            </Badge>
          </div>
          <h1 className="mt-4 text-3xl font-semibold tracking-tight text-white">{text.analyzeTitle}</h1>
          <p className="mt-2 max-w-2xl text-sm leading-7 text-white/60">{text.analyzeBusinessDesc}</p>
        </Card>
        <MarketAnalysisCard lang={lang} />
        <AnalyzePanel initialLang={lang} initialUrl={initialUrl} />
      </div>
    </XBorderLayout>
  );
}
