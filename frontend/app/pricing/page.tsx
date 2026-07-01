import { cookies } from "next/headers";

import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { Card } from "@/design-system/components";
import { PricingCards } from "@/components/billing/pricing-cards";
import { PricingOrdersPanel } from "@/components/billing/pricing-orders-panel";
import { UpgradeEntry } from "@/components/billing/upgrade-entry";
import { TOKEN_KEY } from "@/lib/auth";
import { getBillingOrders, getBillingPlans, getCurrentBillingStatus } from "@/lib/api/billing";
import { isAuthError } from "@/lib/api";
import { getServerLanguage } from "@/lib/i18n-server";

export default async function PricingPage({
  searchParams,
}: {
  searchParams?: Promise<Record<string, string | string[] | undefined>>;
}) {
  const lang = await getServerLanguage();
  const token = (await cookies()).get(TOKEN_KEY)?.value || "";
  const resolvedSearchParams = searchParams ? await searchParams : undefined;
  const payment = typeof resolvedSearchParams?.payment === "string" ? resolvedSearchParams.payment : undefined;
  const orderIdValue = typeof resolvedSearchParams?.order_id === "string" ? Number(resolvedSearchParams.order_id) : NaN;
  const orderId = Number.isFinite(orderIdValue) ? orderIdValue : undefined;

  const [{ plans }, currentPlan, orders] = await Promise.all([
    getBillingPlans(),
    token
      ? getCurrentBillingStatus(token).catch((error) => {
          if (isAuthError(error)) {
            return null;
          }
          throw error;
        })
      : Promise.resolve(null),
    token
      ? getBillingOrders(token).catch((error) => {
          if (isAuthError(error)) {
            return { orders: [] };
          }
          throw error;
        })
      : Promise.resolve({ orders: [] }),
  ]);

  return (
    <XBorderLayout lang={lang} activePath="settings">
      <div className="space-y-6">
        <Card className="border-white/8 bg-[#121c2c] p-6">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <h1 className="text-3xl font-semibold text-white">套餐与订阅</h1>
            <UpgradeEntry label="立即升级" />
          </div>
          <p className="mt-2 text-sm leading-7 text-white/60">
            这里现在已经接入了真实订单创建入口，支持选择支付宝或微信支付。当前还差你的商户参数接入，接好后就能发起真实扣款。
          </p>
          {currentPlan ? (
            <div className="mt-4 rounded-2xl border border-white/8 bg-white/5 px-4 py-3 text-sm text-white/75">
              当前工作区套餐：<span className="font-semibold text-white">{currentPlan.plan_name}</span> · 状态：{currentPlan.status}
            </div>
          ) : (
            <div className="mt-4 rounded-2xl border border-white/8 bg-white/5 px-4 py-3 text-sm text-white/75">
              当前未登录，只展示公开套餐信息。
            </div>
          )}
        </Card>

        <PricingCards plans={plans} currentPlan={currentPlan} />
        <PricingOrdersPanel initialOrders={orders.orders} payment={payment} orderId={orderId} />
      </div>
    </XBorderLayout>
  );
}
