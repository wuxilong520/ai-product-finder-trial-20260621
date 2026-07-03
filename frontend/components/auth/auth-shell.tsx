import Link from "next/link";
import { ArrowLeft, ShieldCheck } from "lucide-react";

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
                { label: "进入系统", value: "登录成功直接进入产品功能首页" },
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
                "如果忘记密码，也可以先用邮箱验证码快速登录。",
                "验证码登录依赖当前环境的邮件通道；如果当前环境没有配好，会明确提示，而不是假装已经发出。",
                "如果账号被封号，会明确提示联系团队，不会静默跳走。",
              ].map((item) => (
                <div key={item} className="flex items-start gap-3 rounded-2xl border border-[#F5E7D4] bg-white/90 p-4">
                  <ShieldCheck className="mt-0.5 h-5 w-5 text-[#F97316]" />
                  <p className="text-sm leading-7 text-[#475569]">{item}</p>
                </div>
              ))}
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
              <CardContent className="p-0">{children}</CardContent>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
