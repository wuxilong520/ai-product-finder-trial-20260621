import Link from "next/link";
import { ArrowRight, BarChart3, CheckCircle2, CirclePlay, DatabaseZap, Gem, ShieldCheck, Sparkles, TrendingUp } from "lucide-react";

import { BrandLockup } from "@/components/branding/brand-lockup";
import { Button, Card, LanguageToggle } from "@/design-system/components";
import { ROUTES } from "@/config/routes";
import { Language } from "@/lib/i18n";
import { LandingAnalyzer } from "@/components/marketing/landing-analyzer";

export function PublicHomeShell({ lang }: { lang: Language }) {
  const topNavItems = [
    { label: "首页能力", href: "#hero" },
    { label: "闭环流程", href: "#flow" },
    { label: "核心页面", href: "#pages" },
    { label: "公开体验", href: "#demo" },
  ];

  const coreAbilities = [
    {
      icon: TrendingUp,
      title: "市场智能",
      desc: "先看类目和关键词到底是在增长还是下滑，再决定这个方向值不值得继续。",
    },
    {
      icon: BarChart3,
      title: "商品机会",
      desc: "把具体商品拉出来比，优先找竞争没那么高、利润空间还不错的机会。",
    },
    {
      icon: DatabaseZap,
      title: "供应链匹配",
      desc: "把 1688 供货、成本、运费、供应商稳定性放在一起看，不只看单个采购价。",
    },
    {
      icon: CirclePlay,
      title: "利润与上架",
      desc: "最后再做利润决策、执行分级和 Shopify 上架准备，不走一上来就乱发货的路。",
    },
  ];

  const loopSteps = [
    {
      step: "01",
      title: "Market",
      desc: "先分析类目和关键词需求，判断是否值得进入。",
    },
    {
      step: "02",
      title: "Opportunity",
      desc: "从市场结果里继续找更值得做的具体商品。",
    },
    {
      step: "03",
      title: "Supply",
      desc: "再去匹配 1688 货源、价格、评分、起订量和稳定性。",
    },
    {
      step: "04",
      title: "Profit",
      desc: "统一算采购、运费、平台费用和利润空间。",
    },
    {
      step: "05",
      title: "Publish",
      desc: "最后才进入 Shopify 执行准备和发布动作。",
    },
  ];

  const productPages = [
    {
      title: "登录后首页",
      desc: "先看今日趋势、热点商品和系统状态，再决定今天先做哪一步。",
      href: ROUTES.login,
    },
    {
      title: "市场智能页",
      desc: "输入关键词，直接看需求分、趋势强度、竞争强度和进入建议。",
      href: ROUTES.login,
    },
    {
      title: "商品机会页",
      desc: "从市场结果继续筛商品，找更有机会做成单品的方向。",
      href: ROUTES.login,
    },
    {
      title: "供应链匹配页",
      desc: "把 1688 货源、价格、评分、MOQ、发货周期统一放进一个页面判断。",
      href: ROUTES.login,
    },
    {
      title: "利润决策页",
      desc: "看 ROI、利润估算、风险等级和执行建议，不再靠拍脑袋做决定。",
      href: ROUTES.login,
    },
    {
      title: "执行页",
      desc: "看 Shopify 草稿、队列、发布状态和执行日志。",
      href: ROUTES.login,
    },
  ];

  const dataCapabilities = [
    "趋势分析：看关键词和类目是在升还是在降。",
    "竞争分析：看当前市场是不是已经太挤。",
    "利润预测：统一看成本、运费、平台费用和利润空间。",
    "风险控制：决定是观察、测试、放量，还是暂时不做。",
  ];

  return (
    <div className="min-h-screen bg-[linear-gradient(180deg,#FFF8F1_0%,#FFFFFF_32%,#FFF7ED_100%)] text-[#0F172A]">
      <div className="mx-auto max-w-7xl px-6 py-8">
        <div className="flex items-center justify-between gap-4">
          <BrandLockup size="sm" darkMode={false} />

          <div className="hidden items-center gap-6 lg:flex">
            {topNavItems.map((item) => (
              <a key={item.label} href={item.href} className="text-sm text-[#64748B] transition hover:text-[#0F172A]">
                {item.label}
              </a>
            ))}
          </div>

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

        <div id="hero" className="grid gap-10 py-12 lg:grid-cols-[1.06fr_0.94fr] lg:items-center">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-[#FED7AA] bg-white px-4 py-2 text-sm text-[#C2410C] shadow-sm">
              <ShieldCheck className="h-4 w-4" />
              AI 驱动 · 市场到上架闭环 · 商业决策系统
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
                { label: "核心能力", value: "市场智能 / 商品机会 / 供应链匹配 / 利润决策" },
                { label: "进入方式", value: "官网体验 → 注册登录 → 进入工作台 → 推进执行" },
              ].map((item) => (
                <div key={item.label} className="rounded-[28px] border border-[#F5E7D4] bg-white p-5 shadow-[0_12px_32px_rgba(15,23,42,0.05)]">
                  <div className="text-sm text-[#64748B]">{item.label}</div>
                  <div className="mt-3 text-base font-semibold leading-7 text-[#0F172A]">{item.value}</div>
                </div>
              ))}
            </div>

            <div className="mt-10 grid gap-4 md:grid-cols-2">
              {coreAbilities.map((item) => {
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

          <div id="demo" className="space-y-5">
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
                "公开体验先让你看懂系统怎么判断",
                "注册登录后再进入完整工作区",
                "真正执行动作放在决策和风控之后",
              ].map((item) => (
                <div key={item} className="flex items-start gap-3 rounded-2xl border border-[#F5E7D4] bg-white px-4 py-4">
                  <CheckCircle2 className="mt-0.5 h-5 w-5 text-[#F97316]" />
                  <p className="text-sm leading-6 text-[#475569]">{item}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div id="flow" className="grid gap-6 border-t border-[#F5E7D4] py-12">
          <div className="max-w-3xl">
            <div className="text-sm font-medium text-[#F97316]">商航AI主流程</div>
            <h2 className="mt-3 text-3xl font-semibold tracking-tight text-[#0F172A]">
              从市场判断开始，一步一步推进到真正能卖
            </h2>
            <p className="mt-3 text-base leading-8 text-[#475569]">
              商航AI不是把所有功能堆在一个页面，而是按真实做跨境生意的顺序往下走：先看市场，再选商品，再找货源，再算利润，最后再准备发布。
            </p>
          </div>

          <div className="grid gap-4 xl:grid-cols-5">
            {loopSteps.map((item) => (
              <div key={item.step} className="rounded-[28px] border border-[#F5E7D4] bg-white p-5 shadow-[0_10px_28px_rgba(15,23,42,0.05)]">
                <div className="inline-flex rounded-full bg-[#FFF7ED] px-3 py-1 text-xs font-semibold text-[#F97316]">
                  STEP {item.step}
                </div>
                <h3 className="mt-4 text-lg font-semibold text-[#0F172A]">{item.title}</h3>
                <p className="mt-2 text-sm leading-7 text-[#475569]">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>

        <div id="pages" className="grid gap-4 border-t border-[#F5E7D4] py-12 lg:grid-cols-[1fr_1fr]">
          <Card className="rounded-[32px] border border-[#F5E7D4] bg-white p-6 shadow-[0_18px_42px_rgba(15,23,42,0.05)]">
            <h3 className="text-2xl font-semibold text-[#0F172A]">登录后会进入的核心页面</h3>
            <div className="mt-5 grid gap-3">
              {productPages.map((item) => (
                <div key={item.title} className="rounded-2xl border border-[#F5E7D4] bg-[#FFFBF7] px-4 py-4">
                  <div className="flex items-center justify-between gap-4">
                    <div>
                      <div className="text-base font-semibold text-[#0F172A]">{item.title}</div>
                      <div className="mt-1 text-sm leading-6 text-[#475569]">{item.desc}</div>
                    </div>
                    <Link href={item.href} className="inline-flex shrink-0 items-center text-sm font-medium text-[#EA580C] hover:text-[#C2410C]">
                      进入
                      <ArrowRight className="ml-2 h-4 w-4" />
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          <Card className="rounded-[32px] border border-[#F5E7D4] bg-[linear-gradient(135deg,#FFF7ED,#FFFFFF)] p-6 shadow-[0_18px_42px_rgba(249,115,22,0.08)]">
            <h3 className="text-2xl font-semibold text-[#0F172A]">官网首页现在负责什么</h3>
            <div className="mt-5 grid gap-3">
              {dataCapabilities.map((item) => (
                <div key={item} className="rounded-2xl border border-[#FED7AA] bg-white px-4 py-3 text-sm text-[#475569]">
                  {item}
                </div>
              ))}
              <div className="rounded-2xl border border-[#FED7AA] bg-white px-4 py-4">
                <div className="flex items-start gap-3">
                  <Gem className="mt-0.5 h-5 w-5 text-[#F97316]" />
                  <div>
                    <div className="text-sm font-semibold text-[#0F172A]">官网首页的目标很明确</div>
                    <div className="mt-1 text-sm leading-6 text-[#475569]">
                      先让用户看懂产品、体验公开分析、进入注册登录，然后再把用户带到真正的产品工作区。
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </Card>
        </div>

        <div className="border-t border-[#F5E7D4] py-12">
          <Card className="rounded-[32px] border border-[#F5E7D4] bg-[linear-gradient(135deg,#FFF7ED,#FFFFFF)] p-8 shadow-[0_18px_42px_rgba(249,115,22,0.08)]">
            <div className="grid gap-6 lg:grid-cols-[1fr_auto] lg:items-center">
              <div>
                <div className="text-sm font-medium text-[#F97316]">下一步动作</div>
                <h3 className="mt-3 text-3xl font-semibold tracking-tight text-[#0F172A]">
                  先注册进入系统，再从市场页开始推进完整闭环
                </h3>
                <p className="mt-3 max-w-3xl text-base leading-8 text-[#475569]">
                  官网首页只负责把用户转进系统。真正做事，是从登录后首页、市场智能页、商品机会页、供应链页、利润决策页一步一步往下走。
                </p>
              </div>
              <div className="flex flex-wrap gap-3">
                <Button asChild size="lg" className="bg-[linear-gradient(135deg,#FB923C,#F97316)] text-white shadow-[0_18px_42px_rgba(249,115,22,0.24)] hover:-translate-y-0.5 hover:shadow-[0_20px_48px_rgba(249,115,22,0.32)]">
                  <Link href={ROUTES.register}>免费注册</Link>
                </Button>
                <Button asChild variant="secondary" size="lg" className="border-[#F5E7D4] bg-white !text-[#334155] hover:border-[#FDBA74] hover:bg-[#FFF7ED] hover:!text-[#0F172A]">
                  <Link href={ROUTES.login}>进入登录页</Link>
                </Button>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
