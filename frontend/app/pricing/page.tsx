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
            <div>
              <div className="text-xs uppercase tracking-[0.24em] text-white/40">商航AI · 套餐与充值中心</div>
              <h1 className="mt-2 text-3xl font-semibold text-white">套餐、充值、订单与能力升级</h1>
            </div>
            <UpgradeEntry label="立即升级" />
          </div>
          <p className="mt-2 text-sm leading-7 text-white/60">
            这里统一管理你的套餐、额度、订单和升级入口。当前页面会真实展示你已有的套餐和订单；支付通道还按现阶段能力逐步收口，不会假装全部已经商用完成。
          </p>
          <div className="mt-4 grid gap-4 md:grid-cols-3">
            <div className="rounded-2xl border border-white/8 bg-white/5 px-4 py-4 text-sm text-white/75">
              <div className="text-xs text-white/45">当前状态</div>
              <div className="mt-2 text-lg font-semibold text-white">{currentPlan ? "已登录工作区" : "公开浏览模式"}</div>
            </div>
            <div className="rounded-2xl border border-white/8 bg-white/5 px-4 py-4 text-sm text-white/75">
              <div className="text-xs text-white/45">当前套餐</div>
              <div className="mt-2 text-lg font-semibold text-white">{currentPlan?.plan_name || "未登录"}</div>
            </div>
            <div className="rounded-2xl border border-white/8 bg-white/5 px-4 py-4 text-sm text-white/75">
              <div className="text-xs text-white/45">支付状态</div>
              <div className="mt-2 text-lg font-semibold text-white">{currentPlan?.status || "仅展示公开套餐"}</div>
            </div>
          </div>
          {token && currentPlan ? (
            <div className="mt-4 grid gap-4 md:grid-cols-3">
              <div className="rounded-2xl border border-white/8 bg-white/5 px-4 py-4 text-sm text-white/75">
                <div className="text-xs text-white/45">当前支付通道</div>
                <div className="mt-2 text-lg font-semibold text-white">微信支付</div>
                <div className="mt-2 text-white/55">当前系统只保留这一条真实支付主线。</div>
              </div>
              <div className="rounded-2xl border border-white/8 bg-white/5 px-4 py-4 text-sm text-white/75">
                <div className="text-xs text-white/45">手动确认支付</div>
                <div className="mt-2 text-lg font-semibold text-white">已关闭</div>
                <div className="mt-2 text-white/55">不会再走手动确认这种假生产路径。</div>
              </div>
              <div className="rounded-2xl border border-white/8 bg-white/5 px-4 py-4 text-sm text-white/75">
                <div className="text-xs text-white/45">当前真实情况</div>
                <div className="mt-2 text-lg font-semibold text-white">订单可创建</div>
                <div className="mt-2 text-white/55">真正扣款能力是否全量商用，要看支付参数是否完全配齐。</div>
              </div>
            </div>
          ) : null}
          <div className="mt-4 grid gap-3 xl:grid-cols-4">
            {[
              "看当前套餐权限",
              "创建升级订单",
              "查看最近支付订单",
              "回到账户中心继续管理",
            ].map((item) => (
              <div key={item} className="rounded-2xl border border-white/8 bg-white/5 px-4 py-3 text-sm text-white/70">
                {item}
              </div>
            ))}
          </div>
        </Card>

        <PricingCards plans={plans} currentPlan={currentPlan} />
        <PricingOrdersPanel initialOrders={orders.orders} payment={payment} orderId={orderId} />
      </div>
    </XBorderLayout>
  );
}
