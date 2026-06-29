export const ROUTES = {
  home: "/",
  login: "/login",
  dashboard: "/",
  products: "/products",
  insights: "/insights",
  actionCenter: "/action-center",
  settings: "/settings",
} as const;

export function productDetailRoute(id: number | string) {
  return `${ROUTES.products}/${id}`;
}

export function analyzeWithProductRoute(productId: number | string) {
  return `${ROUTES.insights}?productId=${productId}`;
}
