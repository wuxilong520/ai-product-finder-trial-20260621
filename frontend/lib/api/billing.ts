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
};

export type CurrentBillingStatus = {
  workspace_id: number;
  plan_name: string;
  status: string;
  updated_at: string;
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
