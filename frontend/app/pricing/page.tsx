import { cookies } from "next/headers";

import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { Card, CardContent, CardHeader, CardTitle, Button } from "@/design-system/components";
import { TOKEN_KEY } from "@/lib/auth";
import { getBillingPlans, getCurrentBillingStatus } from "@/lib/api/billing";
import { getServerLanguage } from "@/lib/i18n-server";

function formatLimit(value: number) {
  if (value < 0) return "不限";
  return `${value}`;
}

export default async function PricingPage() {
  const lang = await getServerLanguage();
  const token = (await cookies()).get(TOKEN_KEY)?.value || "";
  const [{ plans }, currentPlan] = await Promise.all([
    getBillingPlans(),
    token ? getCurrentBillingStatus(token) : Promise.resolve(null),
  ]);

  return (
    <XBorderLayout lang={lang} activePath="settings">
      <div className="space-y-6">
        <Card className="border-white/8 bg-[#121c2c] p-6">
          <h1 className="text-3xl font-semibold text-white">套餐与订阅</h1>
          <p className="mt-2 text-sm leading-7 text-white/60">
            这里先把对外售卖用的套餐结构和当前订阅状态展示出来，后面接入真实支付后就可以直接打通购买。
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

        <div className="grid gap-6 xl:grid-cols-4">
          {plans.map((plan) => (
            <Card key={plan.plan_name} className="border-white/8 bg-[#121c2c]">
              <CardHeader>
                <CardTitle className="capitalize">{plan.plan_name}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="rounded-2xl border border-white/8 bg-white/5 p-4 text-sm text-white/75">
                  <div>每日任务数：{formatLimit(plan.task_limit)}</div>
                  <div className="mt-2">每日接口数：{formatLimit(plan.api_limit)}</div>
                </div>
                <Button className="w-full" variant={plan.plan_name === "pro" ? "primary" : "secondary"}>
                  {plan.plan_name === "free" ? "当前默认体验" : "预留支付接入"}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </XBorderLayout>
  );
}
