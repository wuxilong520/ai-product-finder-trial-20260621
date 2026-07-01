import Link from "next/link";
import { ArrowRight, CheckCircle2, ShieldCheck, Sparkles } from "lucide-react";

import { Button, Card, LanguageToggle } from "@/design-system/components";
import { ROUTES } from "@/config/routes";
import { Language, t } from "@/lib/i18n";
import { LandingAnalyzer } from "@/components/marketing/landing-analyzer";

export function PublicHomeShell({ lang }: { lang: Language }) {
  const text = t(lang);

  return (
    <div className="relative min-h-screen overflow-hidden bg-app-gradient px-6 py-8 text-app-text-primary">
      <div className="absolute inset-0 bg-app-grid opacity-25" />
      <div className="absolute inset-0 bg-app-radial" />

      <div className="relative mx-auto max-w-7xl">
        <div className="flex items-center justify-between gap-4">
          <Link href="/" className="flex items-center gap-3">
            <div className="rounded-2xl bg-app-brand-gradient p-3 text-white shadow-app-glow">
              <Sparkles className="h-5 w-5" />
            </div>
            <div>
              <p className="text-sm text-app-text-muted">XBorder AI</p>
              <p className="text-base font-semibold text-white">跨境商业决策平台</p>
            </div>
          </Link>

          <div className="flex items-center gap-3">
            <LanguageToggle lang={lang} />
            <Button asChild variant="ghost">
              <Link href={ROUTES.login}>登录</Link>
            </Button>
            <Button asChild>
              <Link href={ROUTES.register}>免费注册</Link>
            </Button>
          </div>
        </div>

        <div className="grid gap-8 py-12 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-app-border bg-white/8 px-4 py-2 text-sm text-app-brand-secondary backdrop-blur">
              <ShieldCheck className="h-4 w-4" />
              任务驱动 · 可解释 · 可追溯
            </div>

            <h1 className="gradient-text mt-6 max-w-4xl text-5xl font-semibold tracking-tight">
              先看公开产品首页，登录后再进入你的专属工作台
            </h1>
            <p className="mt-5 max-w-2xl text-lg leading-8 text-app-text-secondary">
              你可以先了解系统怎么跑：市场信号、供应商匹配、成本测算、决策建议、解释和追踪，全部走任务闭环。
            </p>

            <div className="mt-8 flex flex-wrap gap-3">
              <Button asChild size="lg">
                <Link href={ROUTES.register}>
                  我同意并开始注册
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
              <Button asChild variant="secondary" size="lg">
                <Link href={ROUTES.pricing}>查看套餐与模型权限</Link>
              </Button>
            </div>

            <div className="mt-8 grid gap-4 sm:grid-cols-3">
              {[
                "所有核心动作都生成 task_id",
                "结果自带 explain 和 trace",
                "工作区、权限、额度全部隔离",
              ].map((item) => (
                <Card key={item} className="border border-app-border bg-white/6 p-4">
                  <div className="flex items-start gap-3">
                    <CheckCircle2 className="mt-0.5 h-5 w-5 text-app-brand-secondary" />
                    <p className="text-sm leading-6 text-app-text-secondary">{item}</p>
                  </div>
                </Card>
              ))}
            </div>
          </div>

          <Card variant="panel" className="glow-border p-5">
            <div className="rounded-[28px] border border-app-border bg-white/[0.04] p-6">
              <p className="text-sm text-app-text-muted">公开体验区</p>
              <h2 className="mt-3 text-2xl font-semibold text-white">先看一遍真实分析流程</h2>
              <p className="mt-3 text-sm leading-7 text-app-text-secondary">
                这里可以直接体验公开分析卡片。正式任务、充值、权限、工作区等能力，登录后进入工作台使用。
              </p>
              <LandingAnalyzer initialLang={lang} />
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
