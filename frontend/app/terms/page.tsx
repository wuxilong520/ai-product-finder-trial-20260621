import { Card } from "@/design-system/components";

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-[#0B1220] px-6 py-10 text-white">
      <div className="mx-auto max-w-4xl space-y-6">
        <Card className="border-white/8 bg-[#121c2c] p-8">
          <h1 className="text-3xl font-semibold">用户协议</h1>
          <div className="mt-6 space-y-4 text-sm leading-7 text-white/75">
            <p>1. 本系统用于跨境商业判断辅助，不直接代替用户作出最终经营决策。</p>
            <p>2. 用户需保证注册信息真实有效，并自行保管账号、密码、验证码等安全信息。</p>
            <p>3. 未经允许，禁止将系统用于违法、侵权、恶意抓取、攻击性测试等行为。</p>
            <p>4. 套餐权益、配额限制、服务范围以购买页面和服务说明页为准。</p>
            <p>5. 因第三方平台变动、外部数据源异常、网络故障等造成的结果偏差，平台会尽力修复，但不对外部平台本身变化负责。</p>
          </div>
        </Card>
      </div>
    </div>
  );
}
