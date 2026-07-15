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

export type AccountOverview = {
  user: {
    id: number;
    email: string;
    username: string;
    full_name?: string | null;
    role: string;
    status: string;
    workspace_id?: number | null;
    is_active: boolean;
    is_superuser: boolean;
    last_login_at?: string | null;
    failed_login_attempts?: number;
    locked_until?: string | null;
    created_at: string;
    updated_at: string;
  };
  workspace: {
    id: number;
    name: string;
    owner_id: number;
    created_at: string;
    updated_at: string;
  } | null;
  billing: {
    workspace_id: number;
    plan_name: string;
    status: string;
    updated_at: string;
    allowed_ai_providers: string[];
    allowed_ai_models: string[];
    ai_policy_note: string;
    supports_custom_model: boolean;
  };
  recent_orders: Array<{
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
  }>;
  api_key_summary: {
    total_keys: number;
    active_keys: number;
    latest_key_created_at?: string | null;
    latest_key_status?: string | null;
  };
  store_links: {
    shopify: {
      store_base_url_configured: boolean;
      admin_read_ready: boolean;
      execution_mode: string;
      oauth_status: string;
      publish_ready: boolean;
      status_text: string;
      publish_text: string;
    };
  };
  payment_status: {
    wechat_pay: {
      configured: boolean;
      manual_confirm_enabled: boolean;
      checkout_ready: boolean;
      status_text: string;
    };
  };
};

export type AccountApiKeyItem = {
  id: number;
  workspace_id: number;
  user_id: number;
  status: string;
  masked_key: string;
  created_at: string;
  updated_at: string;
};

export async function getAccountOverview(token?: string): Promise<AccountOverview> {
  const apiV1 = getApiV1BaseUrl();
  if (!apiV1) {
    throw new Error("当前没有可用的后端地址，账户信息无法读取");
  }
  const response = await fetch(`${apiV1}/auth/me/overview`, {
    cache: "no-store",
    headers: {
      ...buildAuthHeaders(token),
    },
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "读取账户总览失败"));
  }
  return response.json();
}

export async function getApiKeys(token?: string): Promise<{ items: AccountApiKeyItem[] }> {
  const apiV1 = getApiV1BaseUrl();
  if (!apiV1) {
    throw new Error("当前没有可用的后端地址，API Key 状态无法读取");
  }
  const response = await fetch(`${apiV1}/api-keys`, {
    cache: "no-store",
    headers: {
      ...buildAuthHeaders(token),
    },
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "读取 API Key 失败"));
  }
  return response.json();
}

export async function createApiKey(token?: string): Promise<{
  id: number;
  key: string;
  workspace_id: number;
  user_id: number;
  status: string;
}> {
  const apiV1 = getApiV1BaseUrl();
  if (!apiV1) {
    throw new Error("当前没有可用的后端地址，API Key 无法创建");
  }
  const response = await fetch(`${apiV1}/api-keys`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...buildAuthHeaders(token),
    },
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "创建 API Key 失败"));
  }
  return response.json();
}
