import Link from "next/link";
import { ArrowRight, BarChart3, CheckCircle2, CirclePlay, DatabaseZap, ShieldCheck, Sparkles, Workflow } from "lucide-react";

import { BrandLockup } from "@/components/branding/brand-lockup";
import { Button, Card, LanguageToggle } from "@/design-system/components";
import { ROUTES } from "@/config/routes";
import { Language, t } from "@/lib/i18n";
import { LandingAnalyzer } from "@/components/marketing/landing-analyzer";

export function PublicHomeShell({ lang }: { lang: Language }) {
  const _text = t(lang);

  return (
    <div className="min-h-screen bg-[linear-gradient(180deg,#FFF8F1_0%,#FFFFFF_32%,#FFF7ED_100%)] text-[#0F172A]">
      <div className="mx-auto max-w-7xl px-6 py-8">
        <div className="flex items-center justify-between gap-4">
          <BrandLockup size="sm" darkMode={false} />

          <div className="flex items-center gap-3">
            <LanguageToggle lang={lang} />
            <Button asChild variant="ghost" className="!text-[#64748B] hover:bg-white hover:!text-[#0F172A]">
              <Link href={ROUTES.login}>登录</Link>
            </Button>
            <Button asChild className="bg-[linear-gradient(135deg,#FB923C,#F97316)] text-white shadow-[0_16px_40px_rgba(249,115,22,0.24)] hover:-translate-y-0.5 hover:shadow-[0_18px_44px_rgba(249,115,22,0.3)]">
              <Link href={ROUTES.register}>免费注册</Link>
            </Button>
          </div>
        </div>

        <div className="grid gap-10 py-12 lg:grid-cols-[1.06fr_0.94fr] lg:items-center">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-[#FED7AA] bg-white px-4 py-2 text-sm text-[#C2410C] shadow-sm">
              <ShieldCheck className="h-4 w-4" />
              AI 驱动 · 任务闭环 · 可解释可追溯
            </div>

            <h1 className="mt-6 max-w-4xl text-5xl font-semibold tracking-tight text-[#0F172A]">
              商航AI，帮跨境卖家从
              <span className="text-[#F97316]"> 选品到上架 </span>
              做完整商业决策
            </h1>
            <p className="mt-5 max-w-2xl text-lg leading-8 text-[#475569]">
              它不是普通电商工具，也不是单一数据分析页。商航AI的目标，是把跨境卖家从市场判断、商品选择、供应链匹配、利润测算，到上架执行这整条链路串成一个真正能落地的商业系统。
            </p>

            <div className="mt-8 flex flex-wrap gap-3">
              <Button asChild size="lg" className="bg-[linear-gradient(135deg,#FB923C,#F97316)] text-white shadow-[0_18px_42px_rgba(249,115,22,0.24)] hover:-translate-y-0.5 hover:shadow-[0_20px_48px_rgba(249,115,22,0.32)]">
                <Link href={ROUTES.register}>
                  免费注册体验
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
              <Button asChild variant="secondary" size="lg" className="border-[#F5E7D4] bg-white !text-[#334155] hover:border-[#FDBA74] hover:bg-[#FFF7ED] hover:!text-[#0F172A]">
                <Link href={ROUTES.pricing}>查看套餐与 AI 模型权限</Link>
              </Button>
            </div>

            <div className="mt-8 grid gap-4 sm:grid-cols-3">
              {[
                { label: "闭环流程", value: "Market → Supply → Profit → Publish" },
                { label: "核心能力", value: "市场分析 / 选品决策 / 利润判断 / 上架准备" },
                { label: "进入方式", value: "公开体验 → 注册登录 → 进入产品工作台" },
              ].map((item) => (
                <div key={item.label} className="rounded-[28px] border border-[#F5E7D4] bg-white p-5 shadow-[0_12px_32px_rgba(15,23,42,0.05)]">
                  <div className="text-sm text-[#64748B]">{item.label}</div>
                  <div className="mt-3 text-base font-semibold leading-7 text-[#0F172A]">{item.value}</div>
                </div>
              ))}
            </div>

            <div className="mt-10 grid gap-4 md:grid-cols-2">
              {[
                { icon: BarChart3, title: "市场分析", desc: "先看需求强不强、趋势是涨还是跌、竞争是高还是低，再决定要不要继续做。" },
                { icon: Workflow, title: "选品决策", desc: "对具体商品给出值不值得做、风险高不高、该继续测试还是直接放弃的判断。" },
                { icon: DatabaseZap, title: "利润与供应链", desc: "把供货入口、成本、运费、平台费用放在一起看，而不是只盯一个采购价。" },
                { icon: CirclePlay, title: "上架执行", desc: "确认值得做以后，再进入标题、描述、执行建议和店铺发布准备。" },
              ].map((item) => {
                const Icon = item.icon;
                return (
                  <div key={item.title} className="rounded-[28px] border border-[#F5E7D4] bg-white p-5 shadow-[0_10px_28px_rgba(15,23,42,0.05)]">
                    <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-[#FFF7ED] text-[#F97316]">
                      <Icon className="h-5 w-5" />
                    </div>
                    <h3 className="mt-4 text-lg font-semibold text-[#0F172A]">{item.title}</h3>
                    <p className="mt-2 text-sm leading-7 text-[#475569]">{item.desc}</p>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="space-y-5">
            <Card className="rounded-[32px] border border-[#F5E7D4] bg-white p-6 shadow-[0_24px_60px_rgba(15,23,42,0.08)]">
              <div className="inline-flex items-center gap-2 rounded-full bg-[#FFF7ED] px-3 py-1.5 text-xs font-medium text-[#C2410C]">
                <Sparkles className="h-4 w-4" />
                官网公开体验区
              </div>
              <h2 className="mt-4 text-2xl font-semibold text-[#0F172A]">先看商航AI是怎么给出判断的</h2>
              <p className="mt-3 text-sm leading-7 text-[#475569]">
                这里先给你一个公开体验入口，让你先感受系统怎么做分析。真正的工作区、任务流、供应链、利润、执行链路，要在注册登录后进入产品页使用。
              </p>
              <div className="mt-6 rounded-[28px] border border-[#F5E7D4] bg-[linear-gradient(180deg,#FFFDF9,#FFF7ED)] p-4">
                <LandingAnalyzer initialLang={lang} />
              </div>
            </Card>

            <div className="grid gap-4 sm:grid-cols-3">
              {[
                "任务系统真实运行，不走假同步流程",
                "Explain / Trace / Lineage 会持续收口",
                "真实平台接入会放在最后一阶段",
              ].map((item) => (
                <div key={item} className="flex items-start gap-3 rounded-2xl border border-[#F5E7D4] bg-white px-4 py-4">
                  <CheckCircle2 className="mt-0.5 h-5 w-5 text-[#F97316]" />
                  <p className="text-sm leading-6 text-[#475569]">{item}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="grid gap-6 border-t border-[#F5E7D4] py-12">
          <div className="max-w-3xl">
            <div className="text-sm font-medium text-[#F97316]">商航AI主流程</div>
            <h2 className="mt-3 text-3xl font-semibold tracking-tight text-[#0F172A]">
              从官网进去后，用户会按真实做生意的顺序往下走
            </h2>
            <p className="mt-3 text-base leading-8 text-[#475569]">
              我们不再把它包装成一堆零散功能。用户会先进入官网首页，再注册登录，然后从产品首页出发，依次进入市场分析、商品机会、供应链匹配、利润决策和执行准备。
            </p>
          </div>

          <div className="grid gap-4 xl:grid-cols-5">
            {[
              {
                step: "01",
                title: "官网首页",
                desc: "先让用户看懂商航AI是干什么的，并给出公开体验、注册、登录入口。",
                action: "进入注册 / 登录",
                href: ROUTES.register,
              },
              {
                step: "02",
                title: "登录后首页",
                desc: "先回答今天该看什么，再把用户引到市场页、商品机会页、供应链页、利润页。",
                action: "进入登录页",
                href: ROUTES.login,
              },
              {
                step: "03",
                title: "市场分析页",
                desc: "输入关键词后，先看需求、趋势、竞争、饱和度，再决定要不要继续。",
                action: "先进入系统",
                href: ROUTES.login,
              },
              {
                step: "04",
                title: "商品机会页",
                desc: "基于市场结果，继续筛出更值得做的具体商品，再推到供应链匹配。",
                action: "进入产品页后使用",
                href: ROUTES.login,
              },
              {
                step: "05",
                title: "供应链 → 利润 → 执行",
                desc: "最后再去看供货、利润和上架执行，而不是一上来就直接发布。",
                action: "查看套餐与功能",
                href: ROUTES.login,
              },
            ].map((item) => (
              <div key={item.step} className="rounded-[28px] border border-[#F5E7D4] bg-white p-5 shadow-[0_10px_28px_rgba(15,23,42,0.05)]">
                <div className="inline-flex rounded-full bg-[#FFF7ED] px-3 py-1 text-xs font-semibold text-[#F97316]">
                  STEP {item.step}
                </div>
                <h3 className="mt-4 text-lg font-semibold text-[#0F172A]">{item.title}</h3>
                <p className="mt-2 text-sm leading-7 text-[#475569]">{item.desc}</p>
                <Link href={item.href} className="mt-5 inline-flex items-center text-sm font-medium text-[#EA580C] hover:text-[#C2410C]">
                  {item.action}
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </div>
            ))}
          </div>
        </div>

        <div className="grid gap-4 border-t border-[#F5E7D4] py-12 lg:grid-cols-[1fr_1fr]">
          <Card className="rounded-[32px] border border-[#F5E7D4] bg-white p-6 shadow-[0_18px_42px_rgba(15,23,42,0.05)]">
            <h3 className="text-2xl font-semibold text-[#0F172A]">登录后会进入哪些核心页面</h3>
            <div className="mt-5 grid gap-3">
              {[
                "登录后首页：先看今天该先处理什么机会",
                "市场分析页：先判断需求、趋势、竞争、饱和度",
                "商品机会页：从类目里找更值得做的商品",
                "供应链、利润、执行页：继续推进到真正能卖的动作",
              ].map((item) => (
                <div key={item} className="rounded-2xl border border-[#F5E7D4] bg-[#FFFBF7] px-4 py-3 text-sm text-[#475569]">
                  {item}
                </div>
              ))}
            </div>
          </Card>

          <Card className="rounded-[32px] border border-[#F5E7D4] bg-[linear-gradient(135deg,#FFF7ED,#FFFFFF)] p-6 shadow-[0_18px_42px_rgba(249,115,22,0.08)]">
            <h3 className="text-2xl font-semibold text-[#0F172A]">当前阶段说真话</h3>
            <div className="mt-5 grid gap-3">
              {[
                "官网公开分析体验已经可以直接使用。",
                "注册后自动创建工作区，这个是真实已经接上的。",
                "邮箱验证码是否能真实发到邮箱，取决于当前邮件通道是否已经配置；如果没配置，系统会进入测试投递模式。",
                "Shopify 真实读取能力已经进系统链路，但用户自助绑定和真实发布还没最终收口完成。",
                "1688 和其他真实平台能力还在继续往真实接入推进，不会假装已经全部打通。",
              ].map((item) => (
                <div key={item} className="rounded-2xl border border-[#FED7AA] bg-white px-4 py-3 text-sm text-[#475569]">
                  {item}
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
