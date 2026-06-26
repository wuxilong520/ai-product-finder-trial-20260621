export const ROUTES = {
  home: "/",
  login: "/login",
  dashboard: "/dashboard",
  crawl: "/crawl",
  analyze: "/analyze",
  aiDiscovery: "/ai-discovery",
  marketAnalysis: "/market-analysis",
  supplier: "/supplier",
  operation: "/operation",
  settings: "/settings",
  systemAdmin: "/system/admin",
  productDemo: "/product-demo",
  products: "/product",
  p5Dashboard: "/p5/dashboard",
  p5Recommendations: "/p5/recommendations",
} as const;

export function productDetailRoute(id: number | string) {
  return `${ROUTES.products}/${id}`;
}

export function analyzeWithProductRoute(productId: number | string) {
  return `${ROUTES.analyze}?productId=${productId}`;
}
