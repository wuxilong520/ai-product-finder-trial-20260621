export const ROUTES = {
  home: "/",
  login: "/login",
  register: "/register",
  forgotPassword: "/forgot-password",
  admin: "/admin",
  systemAdmin: "/system/admin",
  pricing: "/pricing",
  terms: "/terms",
  privacy: "/privacy",
  servicePolicy: "/service-policy",
  dashboard: "/",
  products: "/products",
  insights: "/insights",
  actionCenter: "/action-center",
  settings: "/settings",
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
