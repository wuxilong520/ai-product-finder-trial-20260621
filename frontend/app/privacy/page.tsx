import { Card } from "@/design-system/components";

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-[#0B1220] px-6 py-10 text-white">
      <div className="mx-auto max-w-4xl space-y-6">
        <Card className="border-white/8 bg-[#121c2c] p-8">
          <h1 className="text-3xl font-semibold">隐私政策</h1>
          <div className="mt-6 space-y-4 text-sm leading-7 text-white/75">
            <p>1. 平台会收集注册邮箱、登录信息、任务记录、工作区数据，用于提供账号服务和产品功能。</p>
            <p>2. 平台不会在未授权情况下对外出售你的账号信息和业务数据。</p>
            <p>3. 为了保障安全和审计，系统会保留任务日志、解释、追踪、治理记录。</p>
            <p>4. 你可以通过平台设置或联系平台方申请修改账号信息与安全信息。</p>
            <p>5. 如涉及第三方服务（如邮件、支付、平台数据），将遵循对应服务商的合规要求。</p>
          </div>
        </Card>
      </div>
    </div>
  );
}
