import { redirect } from "next/navigation";
import { cookies } from "next/headers";

import { CrawlPanel } from "@/components/products/crawl-panel";
import { ROUTES } from "@/config/routes";
import { Badge, Card } from "@/design-system/components";
import { TOKEN_KEY } from "@/lib/auth";
import { t } from "@/lib/i18n";
import { getServerLanguage } from "@/lib/i18n-server";
import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { ScanSearch, Sparkles } from "lucide-react";

export default async function CrawlPage() {
  const lang = await getServerLanguage();
  const text = t(lang);
  const cookieStore = await cookies();
  const token = cookieStore.get(TOKEN_KEY)?.value || "";
  if (!token) {
    redirect(ROUTES.login);
  }

  return (
    <XBorderLayout lang={lang} activePath="crawl">
      <div className="space-y-5">
        <Card className="border-white/8 bg-[linear-gradient(180deg,rgba(255,255,255,0.04),rgba(255,255,255,0.02))] p-5 shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
          <div className="flex flex-wrap items-center gap-3">
            <Badge variant="brand" className="px-4 py-2 text-sm font-medium">
              <ScanSearch className="h-4 w-4" />
              {text.crawlEyebrow}
            </Badge>
            <Badge variant="neutral" className="px-4 py-2 text-sm text-app-text-secondary">
              <Sparkles className="h-4 w-4 text-app-brand-secondary" />
              {text.dashboardQuickEntryCrawlTitle}
            </Badge>
          </div>
          <h1 className="mt-4 text-3xl font-semibold tracking-tight text-white">{text.crawlTitle}</h1>
          <p className="mt-2 max-w-2xl text-sm leading-7 text-white/60">{text.crawlBusinessDesc}</p>
        </Card>
        <CrawlPanel lang={lang} />
      </div>
    </XBorderLayout>
  );
}
