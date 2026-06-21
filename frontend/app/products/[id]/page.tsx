import { redirect } from "next/navigation";
import { cookies } from "next/headers";

import { AppShell } from "@/components/app-shell";
import { ProductDetail } from "@/components/products/product-detail";
import { analyzeProduct, getProduct } from "@/lib/api";
import { TOKEN_KEY } from "@/lib/auth";
import { getServerLanguage } from "@/lib/i18n-server";

export default async function ProductDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const lang = await getServerLanguage();
  const cookieStore = await cookies();
  const token = cookieStore.get(TOKEN_KEY)?.value || "";
  if (!token) {
    redirect("/login");
  }

  const resolvedParams = await params;
  const product = await getProduct(resolvedParams.id, token);
  let analysisReport = null;
  try {
    analysisReport = await analyzeProduct(Number(resolvedParams.id), token);
  } catch {
    analysisReport = null;
  }

  return (
    <AppShell lang={lang}>
      <ProductDetail product={product} analysisReport={analysisReport} lang={lang} />
    </AppShell>
  );
}
