export const ROUTES = {
  home: "/",
  login: "/login",
  dashboard: "/dashboard",
  crawl: "/crawl",
  analyze: "/analyze",
  productDemo: "/product-demo",
  products: "/products",
} as const;

export function productDetailRoute(id: number | string) {
  return `${ROUTES.products}/${id}`;
}

export function analyzeWithProductRoute(productId: number | string) {
  return `${ROUTES.analyze}?productId=${productId}`;
}
