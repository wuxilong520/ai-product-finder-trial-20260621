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

export type MarketConnectionStatus = {
  connected: boolean;
  status: string;
  permissions?: string[];
  shop_domain?: string | null;
  last_sync?: string | null;
};

export async function getMarketConnections(token?: string): Promise<Record<string, MarketConnectionStatus>> {
  const apiV1 = getApiV1BaseUrl();
  if (!apiV1) {
    throw new Error("当前没有可用的后端地址，连接状态无法读取");
  }
  const response = await fetch(`${apiV1}/market/connections`, {
    cache: "no-store",
    headers: {
      ...buildAuthHeaders(token),
    },
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "读取连接状态失败"));
  }
  return response.json();
}

export async function connectShopify(token: string, shopDomain: string): Promise<{
  authorize_url?: string;
  status?: string;
}> {
  const apiV1 = getApiV1BaseUrl();
  if (!apiV1) {
    throw new Error("当前没有可用的后端地址，Shopify 连接无法启动");
  }
  const response = await fetch(`${apiV1}/market/connect/shopify`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...buildAuthHeaders(token),
    },
    body: JSON.stringify({ shop_domain: shopDomain }),
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "启动 Shopify 授权失败"));
  }
  return response.json();
}
