"use client";

import { useMemo, useState } from "react";

import { Button, Card, CardContent, CardHeader, CardTitle, StatusAlert } from "@/design-system/components";
import { getToken } from "@/lib/auth";
import { createBillingCheckoutOrder, type BillingOrder } from "@/lib/api/billing";

function getStatusText(status: string) {
  if (status === "paid") return "已支付";
  if (status === "failed") return "支付失败";
  if (status === "pending") return "待支付";
  return status;
}

function getStatusTone(status: string): "success" | "warning" | "error" | "blocked" {
  if (status === "paid") return "success";
  if (status === "failed") return "error";
  if (status === "pending") return "warning";
  return "blocked";
}

function buildPaymentNotice(
  payment: string | undefined,
  targetOrder: BillingOrder | null,
) {
  if (payment !== "success" || !targetOrder) return null;
  if (targetOrder.status === "paid") {
    return {
      status: "success" as const,
      title: "支付已完成",
      message: `订单 #${targetOrder.id} 已支付成功，当前套餐已经同步更新。`,
    };
  }
  if (targetOrder.status === "pending") {
    return {
      status: "warning" as const,
      title: "订单还没支付完成",
      message: `订单 #${targetOrder.id} 目前还是待支付，请直接点下方按钮重新发起支付。`,
    };
  }
  return {
    status: "error" as const,
    title: "支付没有完成",
    message: `订单 #${targetOrder.id} 当前状态是“${getStatusText(targetOrder.status)}”，请重新发起支付。`,
  };
}

export function PricingOrdersPanel({
  initialOrders,
  payment,
  orderId,
}: {
  initialOrders: BillingOrder[];
  payment?: string;
  orderId?: number;
}) {
  const [loadingKey, setLoadingKey] = useState("");
  const [error, setError] = useState("");
  const token = useMemo(() => getToken(), []);

  const targetOrder = typeof orderId === "number"
    ? initialOrders.find((item) => item.id === orderId) || null
    : null;
  const notice = buildPaymentNotice(payment, targetOrder);

  async function handleRetry(order: BillingOrder) {
    if (!token) {
      window.location.href = "/login";
      return;
    }
    setError("");
    setLoadingKey(`${order.id}:${order.provider_name || "wechat_pay"}`);
    try {
      const providerName = "wechat_pay";
      const result = await createBillingCheckoutOrder(order.plan_name, providerName, token);
      window.location.href = "/pricing";
    } catch (err) {
      setError(err instanceof Error ? err.message : "重新发起支付失败");
    } finally {
      setLoadingKey("");
    }
  }

  return (
    <div className="space-y-4">
      {notice ? (
        <StatusAlert status={notice.status} title={notice.title} message={notice.message} />
      ) : null}
      {error ? <StatusAlert status="error" message={error} /> : null}

      <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
        <CardHeader>
          <CardTitle>最近支付订单</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {initialOrders.length ? initialOrders.slice(0, 5).map((item) => (
            <div key={item.id} className="rounded-2xl border border-white/8 bg-white/5 p-4 text-sm text-white/75">
              <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                <div>
                  <div className="font-medium text-white">订单 #{item.id}</div>
                  <div className="mt-1">套餐：{item.plan_name} · 状态：{getStatusText(item.status)}</div>
                  <div className="mt-1">支付方式：{item.provider_name || "未指定"} · 金额：{item.currency} {(item.amount_cents / 100).toFixed(2)}</div>
                  {item.note ? <div className="mt-1 text-white/55">{item.note}</div> : null}
                </div>
                {item.status !== "paid" ? (
                  <Button
                    variant={getStatusTone(item.status) === "error" ? "secondary" : "primary"}
                    disabled={loadingKey === `${item.id}:${item.provider_name || "wechat_pay"}`}
                    onClick={() => void handleRetry(item)}
                  >
                    {loadingKey === `${item.id}:${item.provider_name || "wechat_pay"}` ? "处理中..." : "重新发起支付"}
                  </Button>
                ) : null}
              </div>
            </div>
          )) : (
            <div className="rounded-2xl border border-white/8 bg-white/5 p-4 text-sm text-white/60">
              你现在还没有支付订单。点击上面的套餐按钮后，这里会自动出现最新订单。
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
