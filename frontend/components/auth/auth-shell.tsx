import Link from "next/link";
import { ArrowLeft, CheckCircle2, ShieldCheck, TrendingUp, Workflow, Wrench } from "lucide-react";

import { BrandLockup } from "@/components/branding/brand-lockup";
import { Button, Card, CardContent, CardHeader, CardTitle, LanguageToggle } from "@/design-system/components";
import { Language, t } from "@/lib/i18n";

export function AuthShell({
  lang,
  title,
  desc,
  badge,
  children,
}: {
  lang: Language;
  title: string;
  desc: string;
  badge: string;
  children: React.ReactNode;
}) {
  const text = t(lang);
  const loginFlowCards = [
    { icon: TrendingUp, title: "先看机会", desc: "登录后先进入首页，看今天先推进哪个类目和商品。" },
    { icon: Workflow, title: "再走流程", desc: "从市场智能、商品机会、供应链匹配、利润决策一路往下做。" },
    { icon: Wrench, title: "最后执行", desc: "真正上架和发布动作，放在判断完成之后再做。" },
  ];

  return (
    <div className="min-h-screen bg-[linear-gradient(180deg,#FFF9F3_0%,#FFFFFF_38%,#FFF7ED_100%)] px-6 py-8 text-[#0F172A]">
      <div className="mx-auto max-w-7xl">
        <div className="flex items-center justify-between gap-4">
          <BrandLockup size="sm" darkMode={false} />
          <div className="flex items-center gap-3">
            <Button asChild variant="ghost" className="!text-[#64748B] hover:bg-white hover:!text-[#0F172A]">
              <Link href="/">
                <ArrowLeft className="mr-2 h-4 w-4" />
                {text.loginBack}
              </Link>
            </Button>
            <LanguageToggle lang={lang} />
          </div>
        </div>

        <div className="grid gap-10 py-10 lg:grid-cols-[1.02fr_0.98fr] lg:items-start">
          <div className="space-y-8">
            <div className="inline-flex items-center gap-2 rounded-full border border-[#FED7AA] bg-white px-4 py-2 text-sm text-[#C2410C] shadow-sm">
              <ShieldCheck className="h-4 w-4" />
              {badge}
            </div>

            <div>
              <h1 className="max-w-3xl text-5xl font-semibold leading-[1.15] tracking-tight text-[#0F172A]">{title}</h1>
              <p className="mt-5 max-w-2xl text-lg leading-8 text-[#475569]">{desc}</p>
            </div>

            <div className="grid gap-4 sm:grid-cols-3">
              {[
                { label: "登录方式", value: "密码登录 + 邮箱验证码登录" },
                { label: "安全机制", value: "异常情况下会触发额外安全验证" },
                { label: "进入系统", value: "登录成功直接进入商航AI工作台首页" },
              ].map((item) => (
                <div key={item.label} className="rounded-3xl border border-[#F5E7D4] bg-white p-5 shadow-[0_10px_30px_rgba(15,23,42,0.05)]">
                  <div className="text-sm text-[#64748B]">{item.label}</div>
                  <div className="mt-2 text-base font-semibold text-[#0F172A]">{item.value}</div>
                </div>
              ))}
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              {[
                "老用户可以直接用密码登录，适合日常稳定使用。",
                "如果临时不想输密码，也可以用邮箱验证码快速登录。",
                "验证码发送如果失败，页面会直接提示真实结果，不会假装成功。",
                "如果账号被封号，会明确提示联系团队，不会静默跳走。",
              ].map((item) => (
                <div key={item} className="flex items-start gap-3 rounded-2xl border border-[#F5E7D4] bg-white/90 p-4">
                  <ShieldCheck className="mt-0.5 h-5 w-5 text-[#F97316]" />
                  <p className="text-sm leading-7 text-[#475569]">{item}</p>
                </div>
              ))}
            </div>

            <div className="rounded-[32px] border border-[#FED7AA] bg-[linear-gradient(135deg,#FFF7ED,#FFFFFF)] p-6 shadow-[0_18px_48px_rgba(249,115,22,0.08)]">
              <div className="text-sm font-medium text-[#C2410C]">登录后你会怎么用商航AI</div>
              <div className="mt-4 grid gap-3">
                {loginFlowCards.map((item) => {
                  const Icon = item.icon;
                  return (
                    <div key={item.title} className="flex items-start gap-3 rounded-2xl border border-white bg-white px-4 py-4">
                      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-[#FFF7ED] text-[#F97316]">
                        <Icon className="h-4 w-4" />
                      </div>
                      <div>
                        <div className="text-sm font-semibold text-[#0F172A]">{item.title}</div>
                        <div className="mt-1 text-sm leading-6 text-[#475569]">{item.desc}</div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          <Card className="rounded-[32px] border border-[#F5E7D4] bg-white p-6 shadow-[0_24px_60px_rgba(15,23,42,0.08)]">
            <div className="rounded-[28px] border border-[#F3E8D8] bg-[linear-gradient(180deg,#FFFFFF,#FFF9F2)] p-2">
              <CardHeader className="flex flex-row items-center gap-3 px-4 py-4">
                <div className="rounded-2xl bg-white p-2 shadow-[0_12px_30px_rgba(15,23,42,0.18)]">
                  <BrandLockup size="sm" darkMode={false} className="gap-0" />
                </div>
                <div>
                  <p className="text-sm font-medium text-[#F97316]">{text.loginSecure}</p>
                  <CardTitle className="text-lg !text-[#0F172A]">{title}</CardTitle>
                </div>
              </CardHeader>
              <div className="px-4 pb-2 text-sm leading-6 text-[#64748B]">
                登录成功后会直接进入工作台首页，再从市场、商品、供应链、利润、执行页继续往下做。
              </div>
              <CardContent className="p-0">{children}</CardContent>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
