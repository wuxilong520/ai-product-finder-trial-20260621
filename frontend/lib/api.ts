import { AnalyzeFullResponse, AnalyzeResponse, CrawlResult, HealthResponse, LoginResponse, Product, ProductListResponse, PublicExtractResult, TaskStatusResponse, User } from "./types";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  (process.env.NODE_ENV === "development"
    ? "http://127.0.0.1:8000"
    : "https://wuxilong0310-ai-product-finder-backend.hf.space");
const API_V1 = `${API_BASE}/api/v1`;
export const WS_URL =
  process.env.NEXT_PUBLIC_WS_URL ||
  (process.env.NODE_ENV === "development"
    ? "ws://127.0.0.1:8000/ws"
    : "wss://wuxilong0310-ai-product-finder-backend.hf.space/ws");

function ensureApiBase() {
  if (!API_BASE) {
    throw new Error("缺少 NEXT_PUBLIC_API_BASE_URL，当前前端还没连上公网后端");
  }
}

export function getApiBaseUrl() {
  return API_BASE;
}

export function getWsBaseUrl() {
  return WS_URL;
}

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

export async function login(email: string, password: string): Promise<LoginResponse> {
  ensureApiBase();
  const body = new URLSearchParams();
  body.set("username", email);
  body.set("password", password);

  const response = await fetch(`${API_V1}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: body.toString(),
  });

  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "登录失败，请检查账号和密码"));
  }

  return response.json();
}

export async function getCurrentUser(token: string): Promise<User> {
  ensureApiBase();
  const response = await fetch(`${API_V1}/auth/me`, {
    headers: {
      ...buildAuthHeaders(token),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "读取当前用户失败"));
  }

  return response.json();
}

export async function getProducts(search = "", token?: string): Promise<ProductListResponse> {
  ensureApiBase();
  const url = new URL(`${API_V1}/products`);
  if (search) {
    url.searchParams.set("search", search);
  }
  const response = await fetch(url.toString(), {
    cache: "no-store",
    headers: {
      ...buildAuthHeaders(token),
    },
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "读取商品列表失败"));
  }
  return response.json();
}

export async function getProduct(id: string, token?: string): Promise<Product> {
  ensureApiBase();
  const response = await fetch(`${API_V1}/products/${id}`, {
    cache: "no-store",
    headers: {
      ...buildAuthHeaders(token),
    },
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "读取商品详情失败"));
  }
  return response.json();
}

export async function crawlProduct(url: string, token?: string): Promise<CrawlResult> {
  ensureApiBase();
  const response = await fetch(`${API_V1}/products/crawl`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...buildAuthHeaders(token),
    },
    body: JSON.stringify({ url })
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "采集失败"));
  }
  return response.json();
}

export async function extractPublicProduct(url: string): Promise<PublicExtractResult> {
  ensureApiBase();
  const response = await fetch(`${API_V1}/products/extract`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ url }),
  });

  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "解析商品失败"));
  }

  return response.json();
}

export async function analyzeProduct(productId: number, token?: string): Promise<AnalyzeResponse> {
  ensureApiBase();
  const response = await fetch(`${API_V1}/products/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...buildAuthHeaders(token),
    },
    body: JSON.stringify({ product_id: productId })
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "分析失败"));
  }
  return response.json();
}

export async function analyzeTitle(title: string, token?: string): Promise<AnalyzeResponse> {
  ensureApiBase();
  const response = await fetch(`${API_V1}/products/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...buildAuthHeaders(token),
    },
    body: JSON.stringify({ title })
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "分析失败"));
  }
  return response.json();
}

export async function analyzeFull(url: string, lang: "zh" | "en", token?: string): Promise<AnalyzeFullResponse> {
  ensureApiBase();
  const response = await fetch(`${API_V1}/analyze/full`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...buildAuthHeaders(token),
    },
    body: JSON.stringify({ url, lang }),
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "分析失败"));
  }
  return response.json();
}

export async function analyzeFullPublic(url: string, lang: "zh" | "en"): Promise<AnalyzeFullResponse> {
  ensureApiBase();
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 20000);
  try {
    const response = await fetch(`${API_V1}/analyze/full/public`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ url, lang }),
      signal: controller.signal,
    });

    if (!response.ok) {
      throw new Error(await readErrorMessage(response, "分析失败"));
    }

    return response.json();
  } finally {
    clearTimeout(timer);
  }
}

export async function getSystemHealth(): Promise<HealthResponse> {
  ensureApiBase();
  const response = await fetch(`${API_BASE}/health`, {
    cache: "no-store",
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "系统状态读取失败"));
  }
  return response.json();
}

export async function getTaskStatus(taskName: "crawl" | "analyze"): Promise<TaskStatusResponse> {
  ensureApiBase();
  const response = await fetch(`${API_BASE}/task-status/${taskName}`, {
    cache: "no-store",
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "任务状态读取失败"));
  }
  return response.json();
}

export async function deleteProduct(id: number, token?: string): Promise<void> {
  ensureApiBase();
  const response = await fetch(`${API_V1}/products/${id}`, {
    method: "DELETE",
    headers: {
      ...buildAuthHeaders(token),
    },
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "删除失败"));
  }
}
