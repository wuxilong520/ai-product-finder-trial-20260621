"use client";

import { useMemo, useState } from "react";

import { Button, Card, CardContent, CardHeader, CardTitle, StatusAlert } from "@/design-system/components";
import { createApiKey, type AccountApiKeyItem } from "@/lib/api/account";
import { getToken } from "@/lib/auth";

export function ApiKeyPanel({
  initialItems,
}: {
  initialItems: AccountApiKeyItem[];
}) {
  const token = useMemo(() => getToken(), []);
  const [items, setItems] = useState(initialItems);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [createdKey, setCreatedKey] = useState("");

  async function handleCreateKey() {
    if (!token) {
      window.location.href = "/login";
      return;
    }
    setLoading(true);
    setError("");
    setCreatedKey("");
    try {
      const result = await createApiKey(token);
      setCreatedKey(result.key);
      setItems((current) => [
        {
          id: result.id,
          workspace_id: result.workspace_id,
          user_id: result.user_id,
          status: result.status,
          masked_key: `${result.key.slice(0, 8)}...${result.key.slice(-4)}`,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        ...current,
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "创建 API Key 失败");
    } finally {
      setLoading(false);
    }
  }

  async function handleCopyKey() {
    if (!createdKey) return;
    await navigator.clipboard.writeText(createdKey);
  }

  return (
    <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
      <CardHeader className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <CardTitle>API Key 配置</CardTitle>
          <div className="mt-2 text-sm leading-7 text-white/60">
            这里现在能真实查看你已有的 Key 状态，也能新建一个新的 Key。注意：新 Key 只会在创建这一刻完整展示一次。
          </div>
        </div>
        <Button type="button" onClick={() => void handleCreateKey()} disabled={loading}>
          {loading ? "生成中..." : "新建 API Key"}
        </Button>
      </CardHeader>
      <CardContent className="space-y-4">
        {error ? <StatusAlert status="error" message={error} /> : null}
        {createdKey ? (
          <StatusAlert
            status="success"
            title="新的 API Key 已生成"
            message={`请立刻保存：${createdKey}`}
          />
        ) : null}
        {createdKey ? (
          <Button type="button" variant="secondary" onClick={() => void handleCopyKey()}>
            复制刚生成的 API Key
          </Button>
        ) : null}
        <div className="space-y-3">
          {items.length ? items.slice(0, 5).map((item) => (
            <div key={item.id} className="rounded-2xl border border-white/8 bg-white/5 p-4 text-sm text-white/75">
              <div className="font-medium text-white">{item.masked_key}</div>
              <div className="mt-1">状态：{item.status} · 工作区：#{item.workspace_id}</div>
              <div className="mt-1">创建时间：{item.created_at.replace("T", " ").slice(0, 19)}</div>
            </div>
          )) : (
            <div className="rounded-2xl border border-white/8 bg-white/5 p-4 text-sm text-white/60">
              你现在还没有可展示的 API Key 记录。
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
