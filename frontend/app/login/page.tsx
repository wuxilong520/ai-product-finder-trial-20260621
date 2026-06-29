import { LoginForm } from "@/components/auth/login-form";
import { Button, Card, CardContent, CardHeader, CardTitle, LanguageToggle } from "@/design-system/components";
import { t } from "@/lib/i18n";
import { getServerLanguage } from "@/lib/i18n-server";
import Link from "next/link";
import { ArrowLeft, LockKeyhole, ShieldCheck } from "lucide-react";

export default async function LoginPage() {
  const lang = await getServerLanguage();
  const text = t(lang);

  return (
    <div className="relative min-h-screen overflow-hidden bg-app-gradient px-6 py-10 text-app-text-primary">
      <div className="absolute inset-0 bg-app-grid opacity-25" />
      <div className="absolute inset-0 bg-app-radial" />

      <div className="relative mx-auto flex min-h-screen max-w-7xl flex-col">
        <div className="flex items-center justify-between">
          <Button asChild variant="ghost" className="px-0 text-sm">
            <Link href="/">
              <ArrowLeft className="mr-2 h-4 w-4" />
              {text.loginBack}
            </Link>
          </Button>
          <div className="flex items-center gap-3">
            <LanguageToggle lang={lang} />
          </div>
        </div>

        <div className="grid flex-1 items-center gap-10 py-12 lg:grid-cols-[0.92fr_420px]">
          <div className="max-w-2xl">
            <div className="inline-flex items-center gap-2 rounded-full border border-app-border bg-white/8 px-4 py-2 text-sm text-app-brand-secondary backdrop-blur">
              <ShieldCheck className="h-4 w-4" />
              {text.loginBadge}
            </div>

            <h1 className="gradient-text mt-8 max-w-3xl text-5xl font-semibold tracking-tight">
              {text.loginTitle}
            </h1>
            <p className="mt-5 max-w-xl text-lg leading-8 text-app-text-secondary">
              {text.loginDesc}
            </p>

            <div className="mt-8 grid gap-4 sm:grid-cols-2">
              <FeatureBox title={text.loginFeatureExtract} description={text.loginFeature1} />
              <FeatureBox title={text.loginFeatureAnalyze} description={text.loginFeature2} />
            </div>
          </div>

          <Card variant="panel" className="glow-border p-4">
            <div className="rounded-2xl border border-app-border bg-[linear-gradient(180deg,rgba(17,24,39,0.74),rgba(11,15,26,0.96))] p-2 shadow-app-soft">
              <CardHeader className="flex flex-row items-center gap-3 px-4 py-4">
                <div className="rounded-2xl bg-app-brand-gradient p-3 text-white shadow-app-glow">
                  <LockKeyhole className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-sm font-medium text-app-brand-secondary">{text.loginSecure}</p>
                  <CardTitle className="text-lg">{text.loginContinue}</CardTitle>
                </div>
              </CardHeader>
              <CardContent className="p-0">
              <LoginForm lang={lang} />
              </CardContent>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}

function FeatureBox({ title, description }: { title: string; description: string }) {
  return (
    <div className="glass-card rounded-2xl p-5">
      <p className="text-base font-semibold text-white">{title}</p>
      <p className="mt-2 text-sm leading-6 text-app-text-secondary">{description}</p>
    </div>
  );
}
