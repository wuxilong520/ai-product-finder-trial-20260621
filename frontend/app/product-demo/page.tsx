import Link from "next/link";
import { ArrowLeft } from "lucide-react";

import { Button } from "@/design-system/components";
import { ProductDemoPanel } from "@/components/marketing/product-demo-panel";
import { getServerLanguage } from "@/lib/i18n-server";
import { t } from "@/lib/i18n";

export default async function ProductDemoPage() {
  const lang = await getServerLanguage();
  const text = t(lang);

  return (
    <main className="relative min-h-screen overflow-hidden bg-app-gradient text-app-text-primary">
      <div className="absolute inset-0 bg-app-grid opacity-25" />
      <div className="absolute inset-0 bg-app-radial" />

      <div className="relative mx-auto max-w-7xl px-6 py-8">
        <div className="mb-6 flex items-center justify-between">
          <Button asChild variant="ghost">
            <Link href="/">
              <ArrowLeft className="mr-2 h-4 w-4" />
              {text.loginBack}
            </Link>
          </Button>
        </div>

        <ProductDemoPanel initialLang={lang} />
      </div>
    </main>
  );
}
