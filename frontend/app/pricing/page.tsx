import { cookies } from "next/headers";

import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { Card } from "@/design-system/components";
import { PricingCards } from "@/components/billing/pricing-cards";
import { PricingOrdersPanel } from "@/components/billing/pricing-orders-panel";
import { UpgradeEntry } from "@/components/billing/upgrade-entry";
import { TOKEN_KEY } from "@/lib/auth";
import { getAccountOverview } from "@/lib/api/account";
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

  const [{ plans }, currentPlan, orders, overview] = await Promise.all([
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
    token
      ? getAccountOverview(token).catch((error) => {
          if (isAuthError(error)) {
            return null;
          }
          throw error;
        })
      : Promise.resolve(null),
  ]);

  const wechatPay = overview?.payment_status.wechat_pay ?? null;
  const allowedModels = Array.isArray(currentPlan?.allowed_ai_models) ? currentPlan.allowed_ai_models : [];
  const allowedProviders = Array.isArray(currentPlan?.allowed_ai_providers) ? currentPlan.allowed_ai_providers : [];
  const pendingOrders = orders.orders.filter((item) => item.status === "pending").length;
  const nextSteps = [
    currentPlan
      ? {
          title: "先看当前套餐能做什么",
          desc: `你现在用的是 ${currentPlan.plan_name}，先确认模型权限，再决定要不要升级。`,
        }
      : {
          title: "先登录再下单",
          desc: "未登录时这里只展示公开套餐，真正创建订单要先登录工作区。",
        },
    {
      title: pendingOrders > 0 ? "先处理待支付订单" : "可以直接新建升级订单",
      desc: pendingOrders > 0
        ? `你现在还有 ${pendingOrders} 笔待支付订单，建议先处理旧订单，避免重复下单。`
        : "如果你已经确定要升级，可以直接点套餐卡片创建新订单。",
    },
    {
      title: wechatPay?.checkout_ready ? "支付通道已准备好" : "支付通道还没完全收口",
      desc: wechatPay?.checkout_ready
        ? "当前后端返回支付通道可用，可以继续走下单动作。"
        : "当前不假装支付已经完全商用，这里只展示真实状态。",
    },
    {
      title: currentPlan ? "升级后回到工作台继续用" : "先注册登录再继续",
      desc: currentPlan
        ? "买完套餐后，回市场页、商品页、供应链页继续往下做。"
        : "先完成登录，再回这里继续升级和下单。",
    },
  ];

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
          <div className="mt-4 grid gap-3 xl:grid-cols-4">
            {nextSteps.map((item) => (
              <div key={item.title} className="rounded-2xl border border-white/8 bg-white/5 px-4 py-4 text-sm text-white/70">
                <div className="font-medium text-white">{item.title}</div>
                <div className="mt-2 leading-7 text-white/60">{item.desc}</div>
              </div>
            ))}
          </div>
          {token && currentPlan && wechatPay ? (
            <div className="mt-4 grid gap-4 md:grid-cols-3">
              <div className="rounded-2xl border border-white/8 bg-white/5 px-4 py-4 text-sm text-white/75">
                <div className="text-xs text-white/45">当前支付通道</div>
                <div className="mt-2 text-lg font-semibold text-white">{wechatPay.configured ? "微信支付已配置" : "微信支付未配置"}</div>
                <div className="mt-2 text-white/55">{wechatPay.status_text}</div>
              </div>
              <div className="rounded-2xl border border-white/8 bg-white/5 px-4 py-4 text-sm text-white/75">
                <div className="text-xs text-white/45">下单能力</div>
                <div className="mt-2 text-lg font-semibold text-white">{wechatPay.checkout_ready ? "可以创建订单" : "暂时不能正式下单"}</div>
                <div className="mt-2 text-white/55">这个状态直接来自后端支付配置检查。</div>
              </div>
              <div className="rounded-2xl border border-white/8 bg-white/5 px-4 py-4 text-sm text-white/75">
                <div className="text-xs text-white/45">手动确认状态</div>
                <div className="mt-2 text-lg font-semibold text-white">{wechatPay.manual_confirm_enabled ? "仍然打开" : "已经关闭"}</div>
                <div className="mt-2 text-white/55">这里直接展示后端真实返回，不写死。</div>
              </div>
            </div>
          ) : null}
        </Card>

        {currentPlan ? (
          <Card className="border-white/8 bg-[#121c2c] p-6">
            <div className="grid gap-4 md:grid-cols-3">
              <div className="rounded-2xl border border-white/8 bg-white/5 px-4 py-4 text-sm text-white/75">
                <div className="text-xs text-white/45">当前可用模型</div>
                <div className="mt-2 font-medium text-white">{allowedModels.join(" / ") || "未开放"}</div>
              </div>
              <div className="rounded-2xl border border-white/8 bg-white/5 px-4 py-4 text-sm text-white/75">
                <div className="text-xs text-white/45">当前可用通道</div>
                <div className="mt-2 font-medium text-white">{allowedProviders.join(" / ") || "未开放"}</div>
              </div>
              <div className="rounded-2xl border border-white/8 bg-white/5 px-4 py-4 text-sm text-white/75">
                <div className="text-xs text-white/45">最近订单数</div>
                <div className="mt-2 font-medium text-white">{orders.orders.length}</div>
              </div>
            </div>
          </Card>
        ) : null}

        <PricingCards plans={plans} currentPlan={currentPlan} />
        <PricingOrdersPanel initialOrders={orders.orders} payment={payment} orderId={orderId} />
      </div>
    </XBorderLayout>
  );
}
