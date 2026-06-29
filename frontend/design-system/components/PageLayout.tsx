"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Activity, BarChart3, Brain, ChevronRight, LayoutDashboard, LogOut, ScanSearch, Sparkles } from "lucide-react";

import { ROUTES } from "@/config/routes";
import { Badge, StatusBadge } from "@/design-system/components/Badge";
import { Button } from "@/design-system/components/Button";
import { Card } from "@/design-system/components/Card";
import { LanguageToggle } from "@/design-system/components/LanguageToggle";
import { TOKEN_KEY, clearToken } from "@/lib/auth";
import { Language, t } from "@/lib/i18n";
import { cn } from "@/lib/utils";

const navIconClass = "h-4 w-4";

export function PageLayout({ children, lang }: { children: React.ReactNode; lang: Language }) {
  const pathname = usePathname();
  const router = useRouter();
  const text = t(lang);

  const navItems = [
    { href: ROUTES.home, label: "首页", icon: LayoutDashboard },
    { href: ROUTES.products, label: "商品库", icon: ScanSearch },
    { href: ROUTES.insights, label: "市场洞察", icon: Brain },
  ];

  function logout() {
    clearToken();
    document.cookie = `${TOKEN_KEY}=; path=/; max-age=0`;
    router.push(ROUTES.login);
  }

  return (
    <div className="relative isolate min-h-screen bg-app-gradient text-app-text-primary lg:grid lg:grid-cols-[17rem_minmax(0,1fr)]">
      <div className="pointer-events-none absolute inset-0 -z-10 bg-app-grid opacity-30" />
      <div className="pointer-events-none absolute inset-0 -z-10 bg-app-radial" />

      <aside className="relative z-30 hidden h-screen border-r border-app-border bg-app-panel/70 px-5 py-5 backdrop-blur-xl lg:sticky lg:top-0 lg:block">
        <div className="flex h-full flex-col">
          <Card variant="elevated" className="p-5">
            <div className="flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-app-brand-gradient text-white shadow-app-glow">
                <Sparkles className="h-5 w-5" />
              </div>
              <div>
                <p className="text-[11px] uppercase tracking-[0.22em] text-app-text-muted">Cross-border SaaS</p>
                <h1 className="text-lg font-semibold text-white">Product Finder Pro</h1>
              </div>
            </div>
            <Card variant="subtle" className="mt-5 p-4">
              <div className="flex items-center gap-2 text-app-brand-secondary">
                <Activity className="h-4 w-4" />
                <p className="text-sm font-medium">{text.shellBadge}</p>
              </div>
              <p className="mt-2 text-sm leading-6 text-app-text-secondary">{text.shellBadgeDesc}</p>
            </Card>
          </Card>

          <nav className="mt-6 flex-1 space-y-3">
            {navItems.map((item) => {
              const Icon = item.icon;
              const active = pathname === item.href || pathname?.startsWith(`${item.href}/`);

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={(event) => {
                    event.preventDefault();
                    router.push(item.href);
                  }}
                  className={cn(
                    "relative z-10 flex cursor-pointer items-center justify-between rounded-2xl border px-4 py-3 text-sm font-medium transition-all duration-200",
                    active
                      ? "border-app-border-strong bg-white/12 text-white shadow-app-soft"
                      : "border-transparent bg-white/0 text-app-text-secondary hover:-translate-y-0.5 hover:border-app-border hover:bg-white/6 hover:text-white"
                  )}
                >
                  <div className="flex items-center gap-3">
                    <div className={cn("flex h-9 w-9 items-center justify-center rounded-xl", active ? "bg-app-brand-soft text-white" : "bg-white/6 text-app-text-muted")}>
                      <Icon className={navIconClass} />
                    </div>
                    <span>{item.label}</span>
                  </div>
                  <ChevronRight className={cn("h-4 w-4 transition", active ? "text-app-brand-secondary" : "text-app-text-muted/70")} />
                </Link>
              );
            })}
          </nav>

          <Card variant="subtle" className="mt-4 p-3">
            <Button variant="ghost" className="w-full justify-start" onClick={logout}>
              <LogOut className="mr-2 h-4 w-4" />
              {text.logout}
            </Button>
          </Card>
        </div>
      </aside>

      <div className="relative z-10 min-w-0">
        <header className="sticky top-0 z-20 border-b border-app-border bg-app-header/72 backdrop-blur-xl">
          <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-6 py-5">
            <div>
              <p className="text-sm text-app-text-muted">{text.shellTopLine}</p>
              <h2 className="text-3xl font-semibold tracking-tight text-white">{text.shellTopTitle}</h2>
            </div>
            <div className="flex items-center gap-3">
              <LanguageToggle lang={lang} />
              <StatusBadge status="running" label={text.shellLive} />
              <Badge variant="neutral" className="hidden px-4 py-2 text-sm text-app-text-secondary md:inline-flex">
                <BarChart3 className="h-4 w-4 text-app-brand-secondary" />
                {text.shellFlow}
              </Badge>
            </div>
          </div>
        </header>

        <main className="mx-auto max-w-7xl px-6 py-8">{children}</main>
      </div>
    </div>
  );
}
