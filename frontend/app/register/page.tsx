import Link from "next/link";
import { CheckCircle2, ChevronRight, Mail, ShieldCheck, Sparkles } from "lucide-react";

import { BrandLockup } from "@/components/branding/brand-lockup";
import { RegisterForm } from "@/components/auth/register-form";
import { ROUTES } from "@/config/routes";
import { Card } from "@/design-system/components";
import { getServerLanguage } from "@/lib/i18n-server";

export default async function RegisterPage() {
  const lang = await getServerLanguage();

  return (
    <div className="min-h-screen bg-[linear-gradient(180deg,#FFF9F3_0%,#FFFFFF_38%,#FFF7ED_100%)] text-[#0F172A]">
      <div className="mx-auto max-w-7xl px-6 py-8">
        <div className="flex items-center justify-between gap-4">
          <BrandLockup size="sm" darkMode={false} />
          <div className="flex items-center gap-3 text-sm">
            <Link href={ROUTES.home} className="rounded-full px-4 py-2 text-[#64748B] transition hover:bg-white hover:text-[#0F172A]">
              返回官网
            </Link>
            <Link
              href={ROUTES.login}
              className="rounded-full border border-[#FED7AA] bg-white px-4 py-2 text-[#EA580C] shadow-sm transition hover:border-[#FDBA74] hover:bg-[#FFF7ED]"
            >
              已有账号，去登录
            </Link>
          </div>
        </div>

        <div className="grid gap-10 py-10 lg:grid-cols-[1.02fr_0.98fr] lg:items-start">
          <div className="space-y-8">
            <div className="inline-flex items-center gap-2 rounded-full border border-[#FED7AA] bg-white px-4 py-2 text-sm text-[#C2410C] shadow-sm">
              <Sparkles className="h-4 w-4" />
              参考成熟 SaaS 注册页逻辑，先看清价值，再轻松注册
            </div>

            <div>
              <h1 className="max-w-3xl text-5xl font-semibold leading-[1.15] tracking-tight text-[#0F172A]">
                3 分钟完成注册，进入你的
                <span className="text-[#F97316]"> 商航AI 商业决策工作台</span>
              </h1>
              <p className="mt-5 max-w-2xl text-lg leading-8 text-[#475569]">
                注册成功后，系统会自动为你创建专属工作区。后续你就可以围绕选品分析、利润判断、供应链匹配、任务追踪和解释治理，持续使用整套闭环能力。
              </p>
            </div>

            <div className="grid gap-4 sm:grid-cols-3">
              {[
                { label: "注册方式", value: "邮箱验证码 + 密码双保险" },
                { label: "工作区", value: "注册成功自动创建" },
                { label: "初始化", value: "默认 API Key 与免费额度同步初始化" },
              ].map((item) => (
                <div key={item.label} className="rounded-3xl border border-[#F5E7D4] bg-white p-5 shadow-[0_10px_30px_rgba(15,23,42,0.05)]">
                  <div className="text-sm text-[#64748B]">{item.label}</div>
                  <div className="mt-2 text-base font-semibold text-[#0F172A]">{item.value}</div>
                </div>
              ))}
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              {[
                "你可以用邮箱验证码完成注册，后面也支持验证码登录。",
                "系统偶尔会触发安全验证，防止恶意注册和接口滥用。",
                "注册成功后会自动创建默认工作区、默认 API Key，并初始化免费版额度。",
                "如果账号被封号，会明确提示联系团队，不会静默跳转。",
              ].map((item) => (
                <div key={item} className="flex items-start gap-3 rounded-2xl border border-[#F5E7D4] bg-white/90 p-4">
                  <CheckCircle2 className="mt-0.5 h-5 w-5 text-[#F97316]" />
                  <p className="text-sm leading-7 text-[#475569]">{item}</p>
                </div>
              ))}
            </div>

            <div className="rounded-[32px] border border-[#FED7AA] bg-[linear-gradient(135deg,#FFF7ED,#FFFFFF)] p-6 shadow-[0_18px_48px_rgba(249,115,22,0.08)]">
              <div className="flex items-center gap-2 text-sm font-medium text-[#C2410C]">
                <ShieldCheck className="h-4 w-4" />
                注册后你马上能做什么
              </div>
              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                {[
                  "进入登录后首页，看今天先处理什么机会",
                  "进入市场页、商品机会页、供应链页继续往下走",
                  "查看套餐、模型权限、默认 API Key 和账户安全设置",
                  "开始用工作区管理自己的任务与判断结果",
                ].map((item) => (
                  <div key={item} className="flex items-center justify-between rounded-2xl border border-white bg-white px-4 py-3 text-sm text-[#334155]">
                    <span>{item}</span>
                    <ChevronRight className="h-4 w-4 text-[#F97316]" />
                  </div>
                ))}
              </div>
            </div>
          </div>

          <Card className="rounded-[32px] border border-[#F5E7D4] bg-white p-6 shadow-[0_24px_60px_rgba(15,23,42,0.08)]">
            <div className="mb-6 flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-[#FFF7ED] text-[#F97316]">
                <Mail className="h-5 w-5" />
              </div>
              <div>
                <div className="text-sm text-[#64748B]">新用户注册入口</div>
                <h2 className="text-2xl font-semibold text-[#0F172A]">创建你的工作账号</h2>
              </div>
            </div>
            <p className="mb-6 text-sm leading-7 text-[#475569]">
              用邮箱完成注册，系统会自动创建专属工作区。你可以用密码登录，也可以后续用邮箱验证码快捷登录。需要说明的是：验证码能否真实发到邮箱，要看当前环境的邮件通道是否已配置完成。
            </p>
            <RegisterForm lang={lang} />
          </Card>
        </div>
      </div>
    </div>
  );
}
