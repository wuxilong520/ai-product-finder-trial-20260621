export const ROUTES = {
  home: "/",
  login: "/login",
  register: "/register",
  forgotPassword: "/forgot-password",
  admin: "/admin",
  systemAdmin: "/system/admin",
  systemAdminUsers: "/system/admin/users",
  systemAdminRevenue: "/system/admin/revenue",
  pricing: "/pricing",
  terms: "/terms",
  privacy: "/privacy",
  servicePolicy: "/service-policy",
  dashboard: "/",
  products: "/products",
  insights: "/insights",
  actionCenter: "/action-center",
  settings: "/settings",
  productCompare: "/products/compare",
  insightsTrends: "/insights/trends",
  insightsCategories: "/insights/categories",
  insightsOpportunities: "/insights/opportunities",
  insightsBestSellers: "/insights/best-sellers",
  insightsRisks: "/insights/risks",
  insightsForecast: "/insights/forecast",
  actionTopPicks: "/action-center/top-picks",
  actionProfit: "/action-center/profit-review",
  actionSuppliers: "/action-center/suppliers",
  actionPriceCompare: "/action-center/price-compare",
  actionLaunchQueue: "/action-center/launch-queue",
  executionDashboard: "/dashboard/execution",
  productDashboard: "/dashboard/product",
  settingsStoreLinks: "/settings/store-links",
  settingsProfile: "/settings/profile",
  settingsSecurity: "/settings/security",
  tasks: "/tasks",
  createTask: "/create",
} as const;

export function productDetailRoute(id: number | string) {
  return `${ROUTES.products}/${id}`;
}

export function analyzeWithProductRoute(productId: number | string) {
  return `${ROUTES.insights}?productId=${productId}`;
}

export function taskDetailRoute(taskId: number | string) {
  return `${ROUTES.tasks}/${taskId}`;
}
