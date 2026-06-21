import { redirect } from "next/navigation";
import { cookies } from "next/headers";

import { AppShell } from "@/components/app-shell";
import { CrawlPanel } from "@/components/products/crawl-panel";
import { PageHero } from "@/design-system/components";
import { TOKEN_KEY } from "@/lib/auth";
import { t } from "@/lib/i18n";
import { getServerLanguage } from "@/lib/i18n-server";

export default async function CrawlPage() {
  const lang = await getServerLanguage();
  const text = t(lang);
  const cookieStore = await cookies();
  const token = cookieStore.get(TOKEN_KEY)?.value || "";
  if (!token) {
    redirect("/login");
  }

  return (
    <AppShell lang={lang}>
      <PageHero eyebrow={text.crawlEyebrow} title={text.crawlTitle} description={text.crawlDesc} />
      <CrawlPanel lang={lang} />
    </AppShell>
  );
}
