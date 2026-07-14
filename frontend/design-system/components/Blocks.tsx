import Link from "next/link";
import { ArrowRight, ExternalLink, Globe2 } from "lucide-react";

import { Badge, StatusBadge } from "@/design-system/components/Badge";
import { Card, CardContent } from "@/design-system/components/Card";
import { cn } from "@/lib/utils";

export function PageHero({
  eyebrow,
  title,
  description,
  action,
}: {
  eyebrow: string;
  title: string;
  description: string;
  action?: React.ReactNode;
}) {
  return (
    <Card variant="panel" className="mb-6">
      <CardContent className="flex flex-col gap-4 p-6 md:flex-row md:items-center md:justify-between md:p-8">
        <div>
          <p className="text-sm font-medium text-app-brand-secondary">{eyebrow}</p>
          <h2 className="gradient-text mt-2 text-3xl font-semibold tracking-tight">{title}</h2>
          <p className="mt-2 text-sm leading-7 text-app-text-secondary">{description}</p>
        </div>
        {action ? <div className="shrink-0">{action}</div> : null}
      </CardContent>
    </Card>
  );
}

export function InfoTile({ label, value, className }: { label: string; value: string; className?: string }) {
  return (
    <div className={cn("rounded-2xl border border-app-border bg-white/5 p-4 shadow-app-soft", className)}>
      <p className="text-sm text-app-text-muted">{label}</p>
      <p className="mt-2 text-base font-semibold text-white">{value}</p>
    </div>
  );
}

export function MetricTile({ label, value }: { label: string; value: string }) {
  return (
    <Card variant="subtle" className="p-4 transition duration-200 hover:-translate-y-0.5 hover:border-app-border-strong hover:bg-white/8">
      <p className="text-xs uppercase tracking-[0.18em] text-app-text-muted">{label}</p>
      <p className="mt-2 text-lg font-semibold text-white">{value}</p>
    </Card>
  );
}

export function KpiTile({
  label,
  value,
  hint,
  className,
}: {
  label: string;
  value: string;
  hint?: string;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "rounded-3xl border border-app-border bg-[linear-gradient(180deg,rgba(255,255,255,0.08),rgba(255,255,255,0.04))] p-5 shadow-app-soft backdrop-blur-xl",
        className
      )}
    >
      <p className="text-xs uppercase tracking-[0.22em] text-app-text-muted">{label}</p>
      <p className="mt-3 text-3xl font-semibold text-white">{value}</p>
      {hint ? <p className="mt-3 text-sm leading-6 text-app-text-secondary">{hint}</p> : null}
    </div>
  );
}

export function SectionIntro({
  eyebrow,
  title,
  description,
  action,
}: {
  eyebrow?: string;
  title: string;
  description: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
      <div className="max-w-3xl">
        {eyebrow ? <div className="text-xs uppercase tracking-[0.24em] text-app-brand-secondary">{eyebrow}</div> : null}
        <h2 className="mt-2 text-2xl font-semibold tracking-tight text-white md:text-3xl">{title}</h2>
        <p className="mt-3 text-sm leading-7 text-app-text-secondary">{description}</p>
      </div>
      {action ? <div className="shrink-0">{action}</div> : null}
    </div>
  );
}

export function ActionCard({
  title,
  description,
  href,
  label,
  badge,
}: {
  title: string;
  description: string;
  href: string;
  label: string;
  badge?: string;
}) {
  return (
    <Link
      href={href}
      className="group rounded-3xl border border-app-border bg-white/5 p-5 shadow-app-soft transition duration-200 hover:-translate-y-1 hover:border-app-border-strong hover:bg-white/8"
    >
      {badge ? (
        <div className="inline-flex rounded-full border border-app-border bg-white/6 px-3 py-1 text-xs text-app-brand-secondary">
          {badge}
        </div>
      ) : null}
      <div className="mt-3 text-lg font-semibold text-white">{title}</div>
      <div className="mt-3 min-h-[72px] text-sm leading-7 text-app-text-secondary">{description}</div>
      <div className="mt-5 inline-flex items-center gap-2 text-sm font-medium text-app-brand-secondary">
        {label}
        <ArrowRight className="h-4 w-4 transition group-hover:translate-x-0.5" />
      </div>
    </Link>
  );
}

export function SignalCard({
  label,
  value,
  tone = "default",
}: {
  label: string;
  value: string;
  tone?: "default" | "success" | "warning" | "danger";
}) {
  const toneClasses = {
    default: "border-app-border bg-white/5",
    success: "border-emerald-400/20 bg-emerald-400/10",
    warning: "border-amber-400/20 bg-amber-400/10",
    danger: "border-rose-400/20 bg-rose-400/10",
  }[tone];

  return (
    <div className={cn("rounded-2xl border p-4 shadow-app-soft", toneClasses)}>
      <p className="text-sm text-app-text-muted">{label}</p>
      <p className="mt-2 text-lg font-semibold text-white">{value}</p>
    </div>
  );
}

export function EmptyState({
  title,
  text,
  action,
}: {
  title?: string;
  text: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="rounded-3xl border border-dashed border-app-border bg-white/5 px-5 py-10 text-center shadow-app-soft">
      {title ? <div className="text-lg font-semibold text-white">{title}</div> : null}
      <div className={cn("text-sm leading-7 text-app-text-muted", title ? "mt-3" : "")}>{text}</div>
      {action ? <div className="mt-5 flex justify-center">{action}</div> : null}
    </div>
  );
}

export function StatusAlert({
  status,
  title,
  message,
}: {
  status: "running" | "success" | "error" | "warning" | "blocked";
  title?: string;
  message: string;
}) {
  const toneClass = {
    running: "border-teal-400/20 bg-teal-400/10 text-teal-100",
    success: "border-emerald-400/20 bg-emerald-400/10 text-emerald-100",
    error: "border-rose-400/20 bg-rose-400/10 text-rose-200",
    warning: "border-amber-400/20 bg-amber-400/10 text-amber-100",
    blocked: "border-slate-400/20 bg-slate-400/10 text-slate-200",
  }[status];

  return (
    <div className={cn("rounded-2xl border px-4 py-3", toneClass)}>
      {title ? <p className="text-sm font-semibold">{title}</p> : null}
      <p className={cn("text-sm leading-7", title ? "mt-1" : "")}>{message}</p>
    </div>
  );
}

export function TagList({ items, emptyText }: { items: string[]; emptyText?: string }) {
  if (items.length === 0) {
    return <span className="text-sm text-app-text-muted">{emptyText || "Empty"}</span>;
  }

  return (
    <div className="flex flex-wrap gap-2">
      {items.map((item) => (
        <Badge key={item} variant="neutral" className="px-3 py-2 text-sm text-app-text-primary">
          {item}
        </Badge>
      ))}
    </div>
  );
}

export function LinkTile({ href, label }: { href: string; label: string }) {
  return (
    <Link
      href={href}
      target="_blank"
      className="group flex items-center justify-between rounded-2xl border border-app-border bg-white/5 px-4 py-3 no-underline transition hover:-translate-y-0.5 hover:border-app-border-strong hover:bg-white/8 hover:shadow-app-soft"
    >
      <div className="flex items-center gap-3">
        <div className="rounded-xl bg-app-brand-soft p-2 text-app-brand-secondary">
          <Globe2 className="h-4 w-4" />
        </div>
        <span className="font-medium text-white">{label}</span>
      </div>
      <div className="rounded-xl bg-app-brand-gradient p-2 text-white shadow-app-glow transition group-hover:scale-105">
        <ExternalLink className="h-4 w-4" />
      </div>
    </Link>
  );
}

export function ReasonList({ items }: { items: string[] }) {
  return (
    <div className="space-y-3">
      {items.map((item) => (
        <Card key={item} variant="subtle" className="px-4 py-3 text-sm leading-7 text-app-text-secondary">
          {item}
        </Card>
      ))}
    </div>
  );
}

export function StatusSummary({
  label,
  value,
  status,
}: {
  label: string;
  value: string;
  status: "running" | "success" | "error" | "warning" | "blocked";
}) {
  return (
    <div className="flex items-center justify-between gap-4 rounded-2xl border border-app-border bg-white/5 px-4 py-3">
      <div>
        <p className="text-sm text-app-text-muted">{label}</p>
        <p className="mt-2 text-base font-semibold text-white">{value}</p>
      </div>
      <StatusBadge status={status} label={label} />
    </div>
  );
}
