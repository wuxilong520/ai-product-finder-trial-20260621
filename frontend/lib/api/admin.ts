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

export async function getAdminOverview(token?: string): Promise<AdminOverviewResponse> {
  const apiV1 = getApiV1BaseUrl();
  if (!apiV1) {
    throw new Error("当前没有可用的后端地址，后台数据无法读取");
  }
  const response = await fetch(`${apiV1}/admin/overview`, {
    cache: "no-store",
    headers: {
      ...buildAuthHeaders(token),
    },
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "读取后台数据失败"));
  }
  return response.json();
}
