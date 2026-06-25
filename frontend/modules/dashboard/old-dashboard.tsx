import { AppShell } from "@/components/app-shell";
import { ProductList } from "@/components/products/product-list";
import { PageHero } from "@/design-system/components";
import { Language, t } from "@/lib/i18n";
import type { ProductListResponse } from "@/lib/types";

export function OldDashboard({
  lang,
  data,
}: {
  lang: Language;
  data: ProductListResponse;
}) {
  const text = t(lang);

  return (
    <AppShell lang={lang}>
      <PageHero
        eyebrow={text.dashboardEyebrow}
        title={text.dashboardTitle}
        description={text.dashboardDesc}
        action={<div className="rounded-full border border-app-border bg-white/8 px-4 py-2 text-sm text-app-text-secondary shadow-app-soft">{text.dashboardCount.replace("{count}", String(data.total))}</div>}
      />
      <ProductList products={data.items} total={data.total} lang={lang} />
    </AppShell>
  );
}
