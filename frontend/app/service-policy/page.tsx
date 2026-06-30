import { Card } from "@/design-system/components";

export default function ServicePolicyPage() {
  return (
    <div className="min-h-screen bg-[#0B1220] px-6 py-10 text-white">
      <div className="mx-auto max-w-4xl space-y-6">
        <Card className="border-white/8 bg-[#121c2c] p-8">
          <h1 className="text-3xl font-semibold">服务说明</h1>
          <div className="mt-6 space-y-4 text-sm leading-7 text-white/75">
            <p>1. 本系统当前提供任务驱动的市场判断、供应链判断、利润分析、执行建议展示能力。</p>
            <p>2. 不同套餐会限制每日任务数、接口调用数和部分高级功能范围。</p>
            <p>3. 平台当前不直接代用户执行交易、下单、自动运营等动作。</p>
            <p>4. 如因外部平台调整、账号异常、邮件服务故障等问题影响体验，平台会进行维护和公告。</p>
            <p>5. 如需企业版、专属配额、专属支持，可通过商务方式单独沟通。</p>
          </div>
        </Card>
      </div>
    </div>
  );
}
