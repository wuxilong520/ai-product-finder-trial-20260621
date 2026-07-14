"use client";

import { useState } from "react";

import { Button, Card, Input } from "@/design-system/components";
import { connectShopify, type MarketConnectionStatus } from "@/lib/api/market";

export function ShopifyConnectCard({
  token,
  initialConnection,
}: {
  token: string;
  initialConnection?: MarketConnectionStatus;
}) {
  const [shopDomain, setShopDomain] = useState(initialConnection?.shop_domain || "");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleConnect() {
    if (!shopDomain.trim()) {
      setError("先填你的 Shopify 店铺域名");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const result = await connectShopify(token, shopDomain.trim());
      if (result.authorize_url) {
        window.location.href = result.authorize_url;
        return;
      }
      setError("授权地址没有返回");
    } catch (err) {
      setError(err instanceof Error ? err.message : "启动 Shopify 授权失败");
    } finally {
      setLoading(false);
    }
  }

  const connected = !!initialConnection?.connected;

  return (
    <Card className="border-white/8 bg-[#111A2E] p-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="text-sm font-medium text-white">Connect Shopify</div>
          <div className="mt-2 text-sm leading-6 text-white/55">
            {connected ? "当前已连接你的 Shopify 店铺。" : "连接后会同步商品、订单、客户和销售国家。"}
          </div>
          <div className="mt-3 text-sm text-white/60">
            状态：<span className="text-white">{initialConnection?.status || "DISCONNECTED"}</span>
          </div>
          {initialConnection?.last_sync ? (
            <div className="mt-1 text-sm text-white/50">最近同步：{initialConnection.last_sync}</div>
          ) : null}
        </div>
        <div className={`rounded-full px-3 py-1 text-xs ${connected ? "bg-emerald-400/15 text-emerald-200" : "bg-white/10 text-white/70"}`}>
          {connected ? "Connected" : "Connect"}
        </div>
      </div>

      <div className="mt-4 flex flex-col gap-3 md:flex-row">
        <Input
          value={shopDomain}
          onChange={(event) => setShopDomain(event.target.value)}
          placeholder="your-store.myshopify.com"
          className="border-white/10 bg-white/5 text-white placeholder:text-white/30"
        />
        <Button onClick={handleConnect} disabled={loading}>
          {loading ? "连接中..." : connected ? "重新连接 Shopify" : "连接 Shopify 店铺"}
        </Button>
      </div>

      {error ? <div className="mt-3 text-sm text-rose-300">{error}</div> : null}
    </Card>
  );
}
