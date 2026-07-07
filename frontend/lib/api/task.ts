import {
  TaskDetailStatusResponse,
  TaskExplainResponse,
  TaskFullResponse,
  TaskFullResult,
  ExecutionDashboardResponse,
  ProductDashboardResponse,
  TaskListItem,
  TaskSubmitPayload,
  TaskSubmitResponse,
  TaskTraceResponse,
} from "@/lib/types";
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

function ensureTaskApiBase() {
  const apiV1 = getApiV1BaseUrl();
  if (!apiV1) {
    throw new Error("当前没有可用的后端地址，任务系统无法使用");
  }
  return apiV1;
}

function mapSubmitPayloadToBackend(payload: TaskSubmitPayload) {
  return {
    keyword: payload.keyword,
    market_type: payload.market_type,
    supplier_strategy: payload.supplier_strategy,
    cost_mode: payload.cost_mode,
    decision_mode: payload.decision_mode,
  };
}

export async function submitTask(payload: TaskSubmitPayload, token?: string): Promise<TaskSubmitResponse> {
  const apiV1 = ensureTaskApiBase();
  const apiRoot = apiV1.replace(/\/api\/v1$/, "");
  const response = await fetch(`${apiRoot}/api/v1/task/submit`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...buildAuthHeaders(token),
    },
    body: JSON.stringify(mapSubmitPayloadToBackend(payload)),
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "创建任务失败"));
  }
  return response.json();
}

export async function getTaskList(token?: string): Promise<TaskListItem[]> {
  const apiV1 = ensureTaskApiBase();
  const apiRoot = apiV1.replace(/\/api\/v1$/, "");
  const response = await fetch(`${apiRoot}/api/v1/task/list`, {
    cache: "no-store",
    headers: {
      ...buildAuthHeaders(token),
    },
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "读取任务列表失败"));
  }
  return response.json();
}

export async function getTaskStatus(taskId: number, token?: string): Promise<TaskDetailStatusResponse> {
  const apiV1 = ensureTaskApiBase();
  const apiRoot = apiV1.replace(/\/api\/v1$/, "");
  const response = await fetch(`${apiRoot}/api/v1/task/${taskId}`, {
    cache: "no-store",
    headers: {
      ...buildAuthHeaders(token),
    },
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "读取任务状态失败"));
  }
  return response.json();
}

export async function getTaskResult(taskId: number, token?: string): Promise<TaskFullResult> {
  const apiV1 = ensureTaskApiBase();
  const response = await fetch(`${apiV1}/task/${taskId}/result`, {
    cache: "no-store",
    headers: {
      ...buildAuthHeaders(token),
    },
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "读取任务结果失败"));
  }
  return response.json();
}

export async function getTaskExplain(taskId: number, token?: string): Promise<TaskExplainResponse> {
  const apiV1 = ensureTaskApiBase();
  const response = await fetch(`${apiV1}/task/${taskId}/explain`, {
    cache: "no-store",
    headers: {
      ...buildAuthHeaders(token),
    },
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "读取任务解释失败"));
  }
  return response.json();
}

export async function getTaskTrace(taskId: number, token?: string): Promise<TaskTraceResponse> {
  const apiV1 = ensureTaskApiBase();
  const response = await fetch(`${apiV1}/task/${taskId}/trace`, {
    cache: "no-store",
    headers: {
      ...buildAuthHeaders(token),
    },
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "读取任务链路失败"));
  }
  return response.json();
}

export async function getTaskFull(taskId: number, token?: string): Promise<TaskFullResponse> {
  const apiV1 = ensureTaskApiBase();
  const apiRoot = apiV1.replace(/\/api\/v1$/, "");
  const response = await fetch(`${apiRoot}/api/v1/task/${taskId}/full`, {
    cache: "no-store",
    headers: {
      ...buildAuthHeaders(token),
    },
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "读取任务完整结果失败"));
  }
  return response.json();
}

export async function retryTask(taskId: number, token?: string): Promise<TaskSubmitResponse> {
  const apiV1 = ensureTaskApiBase();
  const apiRoot = apiV1.replace(/\/api\/v1$/, "");
  const response = await fetch(`${apiRoot}/api/v1/task/retry/${taskId}`, {
    method: "POST",
    headers: {
      ...buildAuthHeaders(token),
    },
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "重试任务失败"));
  }
  return response.json();
}


export async function getExecutionDashboard(token?: string): Promise<ExecutionDashboardResponse> {
  const apiV1 = ensureTaskApiBase();
  const response = await fetch(`${apiV1}/dashboard/execution`, {
    cache: "no-store",
    headers: {
      ...buildAuthHeaders(token),
    },
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "读取执行看板失败"));
  }
  return response.json();
}


export async function getProductDashboard(token?: string): Promise<ProductDashboardResponse> {
  const apiV1 = ensureTaskApiBase();
  const response = await fetch(`${apiV1}/dashboard/product`, {
    cache: "no-store",
    headers: {
      ...buildAuthHeaders(token),
    },
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "读取产品化总览失败"));
  }
  return response.json();
}
