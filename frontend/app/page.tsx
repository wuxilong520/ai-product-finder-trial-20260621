import Link from "next/link";
import { ArrowRight, BarChart3, Globe2, SearchCheck, Sparkles, TrendingUp } from "lucide-react";

import { ROUTES } from "@/config/routes";
import { Button, Card, CardContent, CardTitle, LanguageToggle, MetricTile, StatusBadge } from "@/design-system/components";
import { LandingAnalyzer } from "@/components/marketing/landing-analyzer";
import { t } from "@/lib/i18n";
import { getServerLanguage } from "@/lib/i18n-server";

export default async function HomePage() {
  const lang = await getServerLanguage();
  const text = t(lang);
  const featureCards = [
    {
      title: text.homeFeature1Title,
      description: text.homeFeature1Desc,
      icon: Globe2,
    },
    {
      title: text.homeFeature2Title,
      description: text.homeFeature2Desc,
      icon: Sparkles,
    },
    {
      title: text.homeFeature3Title,
      description: text.homeFeature3Desc,
      icon: SearchCheck,
    },
  ];
  const statCards = [
    { label: text.homeStat1Label, value: "10x" },
    { label: text.homeStat2Label, value: "100%" },
    { label: text.homeStat3Label, value: "-80%" },
  ];

  return (
    <main className="relative min-h-screen overflow-hidden bg-app-gradient text-app-text-primary">
      <div className="absolute inset-0 bg-app-grid opacity-25" />
      <div className="absolute inset-0 bg-app-radial" />

      <div className="relative mx-auto flex min-h-screen max-w-7xl flex-col px-6 py-8">
        <header className="flex items-center justify-between">
          <div className="glass-card flex items-center gap-3 px-4 py-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-app-brand-gradient text-white shadow-app-glow">
              <TrendingUp className="h-5 w-5" />
            </div>
            <div>
              <p className="text-[11px] uppercase tracking-[0.22em] text-app-brand-secondary">AI Decision Flow</p>
              <h1 className="text-lg font-semibold text-white">XBorder</h1>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Button asChild variant="secondary" className="px-4 py-2 text-sm">
              <Link href={ROUTES.login}>{text.login}</Link>
            </Button>
            <LanguageToggle lang={lang} />
            <Button asChild size="lg">
              <Link href={ROUTES.analyze}>
                {text.startAnalyzing}
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </div>
        </header>

        <section className="grid flex-1 items-center gap-12 py-16 lg:grid-cols-[1.08fr_0.92fr] lg:py-24">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-app-border bg-white/8 px-4 py-2 text-sm text-app-brand-secondary backdrop-blur">
              <BarChart3 className="h-4 w-4" />
              {text.homeBadge}
            </div>

            <h2 className="gradient-text mt-8 max-w-5xl text-5xl font-semibold leading-tight tracking-tight md:text-6xl">
              {text.homeTitle}
            </h2>

            <p className="mt-6 max-w-2xl text-lg leading-8 text-app-text-secondary">{text.homeSubtitle}</p>

            <div className="mt-10 flex flex-col gap-4 sm:flex-row">
              <Button asChild size="lg" className="h-14 px-8 text-base">
                <Link href={ROUTES.analyze}>
                  {text.startAnalyzing}
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
              </Button>
              <Button asChild variant="secondary" size="lg" className="h-14 px-8 text-base">
                <Link href={ROUTES.productDemo}>{text.trialDemoButton}</Link>
              </Button>
              <Button asChild variant="secondary" size="lg" className="h-14 px-8 text-base">
                <Link href={ROUTES.login}>{text.openDashboard}</Link>
              </Button>
            </div>

            <div className="mt-12 grid gap-4 sm:grid-cols-3">
              {statCards.map((item) => (
                <MetricTile key={item.label} label={item.label} value={item.value} />
              ))}
            </div>
          </div>

          <Card variant="panel" className="glow-border p-5">
            <div className="rounded-[24px] border border-app-border bg-white/5 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-app-text-muted">{text.liveSnapshot}</p>
                  <CardTitle className="mt-1 text-xl">{text.decisionPanel}</CardTitle>
                </div>
                <StatusBadge status="running" label={text.online} />
              </div>

              <div className="mt-6 rounded-2xl border border-app-border bg-white/5 p-5">
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <p className="text-sm text-app-text-muted">{text.detailScore}</p>
                    <div className="mt-2 flex items-end gap-3">
                      <span className="text-5xl font-semibold text-white">82</span>
                      <span className="rounded-full border border-emerald-400/18 bg-emerald-400/10 px-3 py-1 text-sm text-emerald-300">
                        {text.recSell}
                      </span>
                    </div>
                  </div>
                  <div className="rounded-2xl border border-app-border bg-white/5 px-4 py-3 text-right">
                    <p className="text-xs uppercase tracking-[0.18em] text-app-text-muted">{text.detailProfit}</p>
                    <p className="mt-2 text-lg font-semibold text-white">$14.8 / order</p>
                  </div>
                </div>

                <div className="mt-6 space-y-4">
                  <div>
                    <div className="mb-2 flex items-center justify-between text-sm text-app-text-secondary">
                      <span>{text.detailCompetition}</span>
                      <span>{text.competitionMedium}</span>
                    </div>
                    <div className="h-2 rounded-full bg-white/8">
                      <div className="h-2 w-[56%] rounded-full bg-[linear-gradient(90deg,#00D2FF,#6C5CE7)]" />
                    </div>
                  </div>

                  <div className="grid gap-3 sm:grid-cols-2">
                    {featureCards.map((card) => {
                      const Icon = card.icon;
                      return (
                        <Card key={card.title} variant="default" className="p-4 transition duration-200 hover:-translate-y-0.5 hover:bg-white/10">
                          <div className="flex items-center gap-3">
                            <div className="rounded-2xl bg-white/10 p-2 text-app-brand-secondary">
                              <Icon className="h-4 w-4" />
                            </div>
                            <p className="text-sm font-medium text-white">{card.title}</p>
                          </div>
                          <p className="mt-3 text-sm leading-6 text-app-text-secondary">{card.description}</p>
                        </Card>
                      );
                    })}
                  </div>
                </div>
              </div>

              <div className="mt-5 grid gap-3 sm:grid-cols-2">
                <Card className="p-4">
                  <p className="text-xs uppercase tracking-[0.18em] text-app-text-muted">{text.supplierLinks}</p>
                  <p className="mt-2 text-base font-medium text-white">{text.sourceLinksReady}</p>
                </Card>
                <Card className="p-4">
                  <p className="text-xs uppercase tracking-[0.18em] text-app-text-muted">{text.speed}</p>
                  <p className="mt-2 text-base font-medium text-white">{text.oneFlowReady}</p>
                </Card>
              </div>
            </div>
          </Card>
        </section>

        <LandingAnalyzer initialLang={lang} />
      </div>
    </main>
  );
}
