import { getApiV1BaseUrl } from "@/lib/api-gateway";

function buildAuthHeaders(token?: string) {
  const headers: Record<string, string> = {};
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  return headers;
}

async function readErrorMessage(response: Response, fallback: string) {
  try {
    const data = await response.json();
    return data.message || data.detail || fallback;
  } catch {
    return fallback;
  }
}

export type BillingPlan = {
  plan_name: string;
  task_limit: number;
  api_limit: number;
  price_cents: number;
  display_price: string;
  allowed_ai_providers: string[];
  allowed_ai_models: string[];
  ai_policy_note: string;
  supports_custom_model: boolean;
};

export type CurrentBillingStatus = {
  workspace_id: number;
  plan_name: string;
  status: string;
  updated_at: string;
  allowed_ai_providers: string[];
  allowed_ai_models: string[];
  ai_policy_note: string;
  supports_custom_model: boolean;
};

export type BillingOrder = {
  id: number;
  workspace_id: number;
  user_id: number | null;
  plan_name: string;
  status: string;
  amount_cents: number;
  currency: string;
  provider_name: string | null;
  external_order_id: string | null;
  note: string | null;
  created_at: string;
  updated_at: string;
};

export type BillingCheckoutResponse = {
  order: BillingOrder;
  payment_ready: boolean;
  payment_message: string;
  payment_payload: Record<string, unknown>;
};

export async function getBillingPlans(): Promise<{ plans: BillingPlan[] }> {
  const apiV1 = getApiV1BaseUrl();
  if (!apiV1) {
    throw new Error("当前没有可用的后端地址，套餐信息无法读取");
  }
  const response = await fetch(`${apiV1}/billing/plans`, {
    cache: "no-store",
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "读取套餐信息失败"));
  }
  return response.json();
}

export async function getCurrentBillingStatus(token?: string): Promise<CurrentBillingStatus> {
  const apiV1 = getApiV1BaseUrl();
  if (!apiV1) {
    throw new Error("当前没有可用的后端地址，当前套餐无法读取");
  }
  const response = await fetch(`${apiV1}/billing/current`, {
    cache: "no-store",
    headers: {
      ...buildAuthHeaders(token),
    },
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "读取当前套餐失败"));
  }
  return response.json();
}

export async function createBillingCheckoutOrder(
  planName: string,
  providerName: "wechat_pay" | "alipay",
  token?: string
): Promise<BillingCheckoutResponse> {
  const apiV1 = getApiV1BaseUrl();
  if (!apiV1) {
    throw new Error("当前没有可用的后端地址，暂时无法创建支付订单");
  }
  const response = await fetch(`${apiV1}/billing/checkout`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...buildAuthHeaders(token),
    },
    body: JSON.stringify({
      plan_name: planName,
      provider_name: providerName,
    }),
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "创建支付订单失败"));
  }
  return response.json();
}

export async function getBillingOrders(token?: string): Promise<{ orders: BillingOrder[] }> {
  const apiV1 = getApiV1BaseUrl();
  if (!apiV1) {
    throw new Error("当前没有可用的后端地址，订单记录无法读取");
  }
  const response = await fetch(`${apiV1}/billing/orders`, {
    cache: "no-store",
    headers: {
      ...buildAuthHeaders(token),
    },
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "读取订单记录失败"));
  }
  return response.json();
}

export async function confirmBillingOrder(orderId: number, token?: string) {
  const apiV1 = getApiV1BaseUrl();
  if (!apiV1) {
    throw new Error("当前没有可用的后端地址，订单确认失败");
  }
  const response = await fetch(`${apiV1}/billing/orders/${orderId}/confirm`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...buildAuthHeaders(token),
    },
    body: JSON.stringify({}),
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "确认订单失败"));
  }
  return response.json();
}
