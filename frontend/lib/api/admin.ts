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

function ensureAdminApi() {
  const apiV1 = getApiV1BaseUrl();
  if (!apiV1) {
    throw new Error("当前没有可用的后端地址，后台数据无法读取");
  }
  return apiV1;
}

export type AdminOverviewResponse = {
  summary: {
    total_users: number;
    total_workspaces: number;
    total_tasks: number;
    paid_workspaces: number;
    free_workspaces: number;
    running_tasks: number;
    failed_tasks: number;
    total_orders: number;
    paid_orders: number;
    revenue_cents: number;
  };
  recent_users: Array<{
    id: number;
    email: string;
    full_name?: string | null;
    role: string;
    workspace_id?: number | null;
    is_active: boolean;
    created_at: string;
  }>;
  recent_workspaces: Array<{
    id: number;
    name: string;
    owner_id: number;
    created_at: string;
  }>;
  recent_tasks: Array<{
    id: number;
    job_type: string;
    status: string;
    retry_count: number;
    workspace_id?: number | null;
    user_id?: number | null;
    updated_at: string;
    last_error?: string | null;
  }>;
  quota_snapshots: Array<{
    workspace_id: number;
    daily_task_limit: number;
    daily_api_limit: number;
    used_task: number;
    used_api: number;
    updated_at: string;
  }>;
  subscription_snapshots: Array<{
    workspace_id: number;
    plan_name: string;
    status: string;
    updated_at: string;
  }>;
  recent_orders: Array<{
    id: number;
    workspace_id: number;
    user_id?: number | null;
    plan_name: string;
    status: string;
    amount_cents: number;
    currency: string;
    provider_name?: string | null;
    updated_at: string;
  }>;
};

export type AdminUserRow = {
  user_id: number;
  contact: string;
  registered_at: string;
  member_level: string;
  api_call_count: number;
  status: "active" | "banned";
  last_login_at?: string | null;
  workspace_id?: number | null;
};

export type AdminRevenueResponse = {
  summary: {
    today_revenue_cents: number;
    month_revenue_cents: number;
    total_revenue_cents: number;
  };
  items: Array<{
    order_id: number;
    user_id?: number | null;
    member_type: string;
    amount_cents: number;
    payment_method?: string | null;
    status: string;
    updated_at: string;
  }>;
};

export type AdminSystemStatusResponse = {
  ai_system: {
    gateway: string;
    deepseek: string;
    openai: string;
    qwen: string;
  };
  api_status: {
    average_response_ms: number;
    error_rate_percent: number;
    fallback_count_24h: number;
    request_count_24h: number;
  };
  server_status: {
    cpu_load_1m: number;
    memory_mb: number;
    network_status: string;
  };
  core_services: Record<string, string>;
};

export async function getAdminOverview(token?: string): Promise<AdminOverviewResponse> {
  const apiV1 = ensureAdminApi();
  const response = await fetch(`${apiV1}/admin/overview`, {
    cache: "no-store",
    headers: buildAuthHeaders(token),
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "读取后台总览失败"));
  }
  return response.json();
}

export async function getAdminUsers(params: {
  token?: string;
  search?: string;
  planName?: string;
  status?: string;
}): Promise<{ items: AdminUserRow[] }> {
  const apiV1 = ensureAdminApi();
  const url = new URL(`${apiV1}/admin/users`);
  if (params.search) url.searchParams.set("search", params.search);
  if (params.planName) url.searchParams.set("plan_name", params.planName);
  if (params.status) url.searchParams.set("status", params.status);
  const response = await fetch(url.toString(), {
    cache: "no-store",
    headers: buildAuthHeaders(params.token),
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "读取用户管理失败"));
  }
  return response.json();
}

export async function banAdminUser(userId: number, token?: string) {
  const apiV1 = ensureAdminApi();
  const response = await fetch(`${apiV1}/admin/users/${userId}/ban`, {
    method: "POST",
    headers: buildAuthHeaders(token),
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "封号失败"));
  }
  return response.json();
}

export async function unbanAdminUser(userId: number, token?: string) {
  const apiV1 = ensureAdminApi();
  const response = await fetch(`${apiV1}/admin/users/${userId}/unban`, {
    method: "POST",
    headers: buildAuthHeaders(token),
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "解封失败"));
  }
  return response.json();
}

export async function changeAdminUserMembership(userId: number, planName: string, token?: string) {
  const apiV1 = ensureAdminApi();
  const response = await fetch(`${apiV1}/admin/users/${userId}/membership`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...buildAuthHeaders(token),
    },
    body: JSON.stringify({ plan_name: planName }),
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "修改会员失败"));
  }
  return response.json();
}

export async function resetAdminUserApiKey(userId: number, token?: string) {
  const apiV1 = ensureAdminApi();
  const response = await fetch(`${apiV1}/admin/users/${userId}/reset-api-key`, {
    method: "POST",
    headers: buildAuthHeaders(token),
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "重置 API Key 失败"));
  }
  return response.json();
}

export async function getAdminRevenue(params: {
  token?: string;
  startDate?: string;
  endDate?: string;
  userId?: string;
  planName?: string;
}): Promise<AdminRevenueResponse> {
  const apiV1 = ensureAdminApi();
  const url = new URL(`${apiV1}/admin/revenue`);
  if (params.startDate) url.searchParams.set("start_date", params.startDate);
  if (params.endDate) url.searchParams.set("end_date", params.endDate);
  if (params.userId) url.searchParams.set("user_id", params.userId);
  if (params.planName) url.searchParams.set("plan_name", params.planName);
  const response = await fetch(url.toString(), {
    cache: "no-store",
    headers: buildAuthHeaders(params.token),
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "读取收入管理失败"));
  }
  return response.json();
}

export async function getAdminSystemStatus(token?: string): Promise<AdminSystemStatusResponse> {
  const apiV1 = ensureAdminApi();
  const response = await fetch(`${apiV1}/admin/system-status`, {
    cache: "no-store",
    headers: buildAuthHeaders(token),
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "读取系统状态失败"));
  }
  return response.json();
}
