import {
  AnalyzeFullResponse,
  AnalyzeResponse,
  BusinessTruthRecommendResponse,
  CrawlResult,
  DecisionV1Payload,
  DecisionV1Response,
  DecisionRecommendResponse,
  DashboardSourcesResponse,
  DashboardSummaryResponse,
  DashboardTasksResponse,
  DashboardTrendsResponse,
  HealthResponse,
  ListingV1Payload,
  ListingV1Response,
  LoginResponse,
  MarketAnalyzeResponse,
  OpportunityAnalyzeResponse,
  OpportunityExecuteResponse,
  OpportunityHistoryResponse,
  Product,
  ProductBatchDeleteResponse,
  ProductIntelligenceEngineResponse,
  ProductListResponse,
  PublicExtractResult,
  P5PredictionResponse,
  P5RankingsResponse,
  P5RecommendationsResponse,
  PublishV1Payload,
  PublishV1Response,
  SupplierMatchResponse,
  SupplyExtensionCodeResponse,
  SupplyExtensionImportPayload,
  SupplyExtensionImportResponse,
  SupplyExtensionSessionResponse,
  SendCodeResponse,
  TaskStatusResponse,
  User,
} from "./types";

function trimTrailingSlash(value: string) {
  return value.replace(/\/+$/, "");
}

const RAW_API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "";
const API_BASE = trimTrailingSlash(RAW_API_BASE);
const API_ROOT = API_BASE.endsWith("/api/v1") ? API_BASE.replace(/\/api\/v1$/, "") : API_BASE;
const API_V1 = API_BASE.endsWith("/api/v1") ? API_BASE : `${API_BASE}/api/v1`;
const RAW_WS_URL = process.env.NEXT_PUBLIC_WS_URL || "";
export const WS_URL = trimTrailingSlash(RAW_WS_URL);

function ensureApiBase() {
  if (!API_BASE) {
    throw new Error("缺少 NEXT_PUBLIC_API_BASE，当前前端还没连上公网后端");
  }
}

export function getApiBaseUrl() {
  return API_BASE;
}

export function getApiRootUrl() {
  return API_ROOT;
}

export function getApiV1BaseUrl() {
  return API_V1;
}

export function getWsBaseUrl() {
  return WS_URL;
}

export function isNewDashboardEnabled() {
  return process.env.NEXT_PUBLIC_ENABLE_NEW_DASHBOARD === "true";
}

export function isAuthError(error: unknown) {
  if (!(error instanceof Error)) {
    return false;
  }
  return /token|登录|认证|unauthorized|forbidden|401|403|未登录|失效|无效|权限|用户不存在|已停用/i.test(error.message);
}

export function isBannedError(error: unknown) {
  if (!(error instanceof Error)) {
    return false;
  }
  return /封号|封禁|banned/i.test(error.message);
}

function buildAuthHeaders(token?: string) {
  const headers: Record<string, string> = {};
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  return headers;
}

async function fetchWithTimeout(input: RequestInfo | URL, init: RequestInit = {}, timeoutMs = 15000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(input, {
      ...init,
      signal: controller.signal,
    });
  } catch (error) {
    if (error instanceof Error && error.name === "AbortError") {
      throw new Error("请求超时，请确认前端和后端服务都已启动");
    }
    if (error instanceof Error) {
      throw new Error(`网络连接失败：${error.message}`);
    }
    throw new Error("网络连接失败，请稍后重试");
  } finally {
    clearTimeout(timer);
  }
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

  const response = await fetchWithTimeout(`${API_V1}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: body.toString(),
  }, 15000);

  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "登录失败，请检查账号和密码"));
  }

  return response.json();
}

export async function loginWithCode(email: string, code: string): Promise<LoginResponse> {
  ensureApiBase();
  const response = await fetchWithTimeout(`${API_V1}/auth/login/code`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, code }),
  }, 15000);

  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "验证码登录失败"));
  }

  return response.json();
}

export async function registerUser(email: string, password: string, verificationCode: string, fullName?: string): Promise<User> {
  ensureApiBase();
  const response = await fetchWithTimeout(`${API_V1}/auth/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email,
      password,
      verification_code: verificationCode,
      full_name: fullName || null,
    }),
  }, 15000);

  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "注册失败"));
  }

  return response.json();
}

export async function sendAuthCode(
  email: string,
  purpose: "login" | "register" | "reset_password",
  challengeToken?: string,
  challengeAnswer?: string
): Promise<SendCodeResponse> {
  ensureApiBase();

  const response = await fetchWithTimeout(`${API_V1}/auth/send-code`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email,
      purpose,
      challenge_token: challengeToken || null,
      challenge_answer: challengeAnswer || null,
    }),
  }, 15000);

  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "发送验证码失败"));
  }

  return response.json();
}

export async function resetPassword(email: string, code: string, newPassword: string): Promise<{ success: boolean; message: string }> {
  ensureApiBase();
  const response = await fetchWithTimeout(`${API_V1}/auth/password/reset`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email,
      code,
      new_password: newPassword,
    }),
  }, 15000);

  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "重置密码失败"));
  }

  return response.json();
}

export async function createSupplyExtensionCode(token: string): Promise<SupplyExtensionCodeResponse> {
  ensureApiBase();
  const response = await fetchWithTimeout(`${API_V1}/supply/extension/code`, {
    method: "POST",
    headers: {
      ...buildAuthHeaders(token),
    },
  }, 15000);
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "生成插件连接码失败"));
  }
  return response.json();
}

export async function createSupplyExtensionSession(extensionCode: string): Promise<SupplyExtensionSessionResponse> {
  ensureApiBase();
  const response = await fetchWithTimeout(`${API_V1}/supply/extension/session`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ extension_code: extensionCode }),
  }, 15000);
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "插件连接失败"));
  }
  return response.json();
}

export async function importSupplyExtensionPayload(
  extensionToken: string,
  payload: SupplyExtensionImportPayload
): Promise<SupplyExtensionImportResponse> {
  ensureApiBase();
  const response = await fetchWithTimeout(`${API_V1}/supply/extension/import`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${extensionToken}`,
    },
    body: JSON.stringify(payload),
  }, 30000);
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "插件同步供应商数据失败"));
  }
  return response.json();
}

export async function getCurrentUser(token: string): Promise<User> {
  ensureApiBase();
  const response = await fetchWithTimeout(`${API_V1}/auth/me`, {
    headers: {
      ...buildAuthHeaders(token),
    },
    cache: "no-store",
  }, 15000);

  if (!response.ok) {
    const message = await readErrorMessage(response, "读取当前用户失败");
    throw new Error(`[${response.status}] ${message}`);
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

export async function getProductIntelligence(id: string | number, token?: string): Promise<ProductIntelligenceEngineResponse> {
  ensureApiBase();
  const response = await fetch(`${API_V1}/products/${id}/intelligence`, {
    cache: "no-store",
    headers: {
      ...buildAuthHeaders(token),
    },
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "读取商品情报失败"));
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

export async function analyzeMarketKeyword(keyword: string, token?: string): Promise<MarketAnalyzeResponse> {
  ensureApiBase();
  const response = await fetch(`${API_V1}/market/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...buildAuthHeaders(token),
    },
    body: JSON.stringify({ keyword }),
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "市场分析失败"));
  }
  return response.json();
}

export async function matchSuppliers(keyword: string, token?: string): Promise<SupplierMatchResponse> {
  ensureApiBase();
  const response = await fetch(`${API_V1}/suppliers/match`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...buildAuthHeaders(token),
    },
    body: JSON.stringify({ keyword }),
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "供应链匹配失败"));
  }
  return response.json();
}

export async function analyzeOpportunity(
  payload: {
    keyword: string;
    marketplace?: string;
    region?: string;
  },
  token?: string,
): Promise<OpportunityAnalyzeResponse> {
  ensureApiBase();
  const response = await fetch(`${API_V1}/opportunity/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...buildAuthHeaders(token),
    },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "商业机会分析失败"));
  }
  return response.json();
}

export async function executeOpportunity(
  payload: {
    keyword: string;
    marketplace?: string;
    region?: string;
    shop_domain: string;
  },
  token?: string,
): Promise<OpportunityExecuteResponse> {
  ensureApiBase();
  const response = await fetch(`${API_V1}/opportunity/execute`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...buildAuthHeaders(token),
    },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "商业机会执行失败"));
  }
  return response.json();
}

export async function getOpportunityHistory(token?: string, limit = 20): Promise<OpportunityHistoryResponse> {
  ensureApiBase();
  const response = await fetch(`${API_V1}/opportunity/history?limit=${limit}`, {
    method: "GET",
    headers: {
      ...buildAuthHeaders(token),
    },
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "商业机会历史读取失败"));
  }
  return response.json();
}

export async function recommendDecision(productId: number, token?: string): Promise<DecisionRecommendResponse> {
  ensureApiBase();
  const response = await fetch(`${API_V1}/decision/recommend`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...buildAuthHeaders(token),
    },
    body: JSON.stringify({ product_id: productId }),
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "决策推荐失败"));
  }
  return response.json();
}

export async function recommendBusinessTruth(productId: number, token?: string): Promise<BusinessTruthRecommendResponse> {
  ensureApiBase();
  const response = await fetch(`${API_V1}/business-truth/recommend`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...buildAuthHeaders(token),
    },
    body: JSON.stringify({ product_id: productId }),
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "商业真实性评分失败"));
  }
  return response.json();
}

export async function runDecisionV1(payload: DecisionV1Payload, token?: string): Promise<DecisionV1Response> {
  ensureApiBase();
  const response = await fetch(`${API_V1}/decision`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...buildAuthHeaders(token),
    },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "利润决策失败"));
  }
  const data = await response.json();
  return data.data;
}

export async function runListingV1(payload: ListingV1Payload, token?: string): Promise<ListingV1Response> {
  ensureApiBase();
  const response = await fetch(`${API_V1}/listing`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...buildAuthHeaders(token),
    },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "上架草稿生成失败"));
  }
  const data = await response.json();
  return data.data;
}

export async function runPublishV1(payload: PublishV1Payload, token?: string): Promise<PublishV1Response> {
  ensureApiBase();
  const response = await fetch(`${API_V1}/publish`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...buildAuthHeaders(token),
    },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "发布检查失败"));
  }
  const data = await response.json();
  return data.data;
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
  const timer = setTimeout(() => controller.abort(), 180000);
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
  } catch (error) {
    if (error instanceof Error && (error.name === "AbortError" || /aborted/i.test(error.message))) {
      throw new Error("分析时间太长，当前请求已超时。请稍等一下再试，或者换一个更容易打开的公开商品页。");
    }
    if (error instanceof Error) {
      throw new Error(`分析请求失败：${error.message}`);
    }
    throw new Error("分析请求失败，请稍后重试");
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

export async function getDashboardSummary(token?: string): Promise<DashboardSummaryResponse> {
  ensureApiBase();
  const response = await fetch(`${API_V1}/dashboard/summary`, {
    cache: "no-store",
    headers: {
      ...buildAuthHeaders(token),
    },
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "读取看板概览失败"));
  }
  return response.json();
}

export async function getDashboardTrends(token?: string): Promise<DashboardTrendsResponse> {
  ensureApiBase();
  const response = await fetch(`${API_V1}/dashboard/trends`, {
    cache: "no-store",
    headers: {
      ...buildAuthHeaders(token),
    },
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "读取趋势失败"));
  }
  return response.json();
}

export async function getDashboardTasks(token?: string): Promise<DashboardTasksResponse> {
  ensureApiBase();
  const response = await fetch(`${API_V1}/dashboard/tasks`, {
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

export async function getDashboardSources(token?: string): Promise<DashboardSourcesResponse> {
  ensureApiBase();
  const response = await fetch(`${API_V1}/dashboard/sources`, {
    cache: "no-store",
    headers: {
      ...buildAuthHeaders(token),
    },
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "读取数据源状态失败"));
  }
  return response.json();
}

export async function getP5Rankings(token?: string): Promise<P5RankingsResponse> {
  ensureApiBase();
  const response = await fetch(`${API_V1}/p5/rankings`, {
    cache: "no-store",
    headers: {
      ...buildAuthHeaders(token),
    },
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "读取 P5 排行失败"));
  }
  return response.json();
}

export async function getP5Recommendations(params: { keyword?: string; category?: string; limit?: number }, token?: string): Promise<P5RecommendationsResponse> {
  ensureApiBase();
  const url = new URL(`${API_V1}/p5/recommendations`);
  if (params.keyword) {
    url.searchParams.set("keyword", params.keyword);
  }
  if (params.category) {
    url.searchParams.set("category", params.category);
  }
  if (params.limit) {
    url.searchParams.set("limit", String(params.limit));
  }
  const response = await fetch(url.toString(), {
    cache: "no-store",
    headers: {
      ...buildAuthHeaders(token),
    },
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "读取 P5 推荐失败"));
  }
  return response.json();
}

export async function predictP5Product(productId: number, horizonDays = 30, token?: string): Promise<P5PredictionResponse> {
  ensureApiBase();
  const response = await fetch(`${API_V1}/p5/predict`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...buildAuthHeaders(token),
    },
    body: JSON.stringify({
      product_id: productId,
      horizon_days: horizonDays,
    }),
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "读取 P5 预测失败"));
  }
  return response.json();
}

export async function batchDeleteProducts(productIds: number[], token?: string): Promise<ProductBatchDeleteResponse> {
  ensureApiBase();
  const response = await fetch(`${API_V1}/products/batch-delete`, {
    method: "DELETE",
    headers: {
      "Content-Type": "application/json",
      ...buildAuthHeaders(token),
    },
    body: JSON.stringify({ product_ids: productIds }),
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "批量删除失败"));
  }
  return response.json();
}
