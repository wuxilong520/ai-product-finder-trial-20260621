"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";

import { Button, Card, CardContent, CardHeader, CardTitle, StatusAlert } from "@/design-system/components";
import { getToken } from "@/lib/auth";
import { createBillingCheckoutOrder, type BillingPlan, type CurrentBillingStatus } from "@/lib/api/billing";

function formatLimit(value: number) {
  if (value < 0) return "不限";
  return `${value}`;
}

export function PricingCards({
  plans,
  currentPlan,
}: {
  plans: BillingPlan[];
  currentPlan: CurrentBillingStatus | null;
}) {
  const [loadingKey, setLoadingKey] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [latestOrderId, setLatestOrderId] = useState<number | null>(null);
  const token = useMemo(() => getToken(), []);
  const router = useRouter();

  async function handleCheckout(planName: string, providerName: "wechat_pay") {
    if (!token) {
      router.push("/login");
      return;
    }
    setLoadingKey(`${planName}:${providerName}`);
    setError("");
    setMessage("");
    try {
      const result = await createBillingCheckoutOrder(planName, providerName, token);
      setLatestOrderId(result.order.id);
      setMessage(`订单 #${result.order.id} 已创建，支付方式：微信支付。${result.payment_message}`);
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "创建订单失败");
    } finally {
      setLoadingKey("");
    }
  }

  return (
    <div className="space-y-6">
      {error ? <StatusAlert status="error" message={error} /> : null}
      {message ? <StatusAlert status="success" message={message} /> : null}
      {latestOrderId ? (
        <div className="rounded-2xl border border-[#4F7CFF]/20 bg-[#4F7CFF]/10 px-4 py-3 text-sm text-[#D8E3FF]">
          最近一次套餐订单：#{latestOrderId}。页面已自动刷新当前套餐和订单区块，你可以往下直接看变化。
        </div>
      ) : null}

      <div className="grid gap-6 xl:grid-cols-4">
        {plans.map((plan) => {
          const isCurrent = currentPlan?.plan_name === plan.plan_name;
          return (
            <Card key={plan.plan_name} className="border-white/8 bg-[#121c2c]">
              <CardHeader>
                <CardTitle className="capitalize">{plan.plan_name}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="rounded-2xl border border-white/8 bg-white/5 p-4 text-sm text-white/75">
                  <div className="text-lg font-semibold text-white">{plan.display_price}</div>
                  <div className="mt-3">每日任务数：{formatLimit(plan.task_limit)}</div>
                  <div className="mt-2">每日接口数：{formatLimit(plan.api_limit)}</div>
                  <div className="mt-2">可用模型：{plan.allowed_ai_models.join(" / ") || "未开放"}</div>
                  <div className="mt-2">可用通道：{plan.allowed_ai_providers.join(" / ") || "未开放"}</div>
                  <div className="mt-3 text-white/55">{plan.ai_policy_note}</div>
                  {plan.supports_custom_model ? <div className="mt-2 text-xs text-[#9CC0FF]">支持企业专属模型接入</div> : null}
                </div>

                {isCurrent ? (
                  <Button className="w-full" variant="secondary" disabled>
                    当前套餐
                  </Button>
                ) : plan.plan_name === "free" ? (
                  <Button className="w-full" variant="secondary" disabled>
                    默认体验
                  </Button>
                ) : (
                  <div className="space-y-3">
                    <Button
                      className="w-full"
                      variant="primary"
                      disabled={loadingKey === `${plan.plan_name}:wechat_pay`}
                      onClick={() => void handleCheckout(plan.plan_name, "wechat_pay")}
                    >
                      {loadingKey === `${plan.plan_name}:wechat_pay` ? "创建中..." : "微信支付购买"}
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
