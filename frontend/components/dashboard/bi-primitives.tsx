"use client";

import { cn } from "@/lib/utils";

export function DashboardSection({
  title,
  subtitle,
  action,
  children,
  className,
}: {
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <section className={cn("rounded-[20px] border border-white/8 bg-[linear-gradient(180deg,rgba(18,28,44,0.96),rgba(11,18,31,0.98))] shadow-[0_18px_40px_rgba(0,0,0,0.22)]", className)}>
      <div className="flex items-start justify-between gap-4 border-b border-white/8 px-6 py-5">
        <div>
          <h2 className="text-lg font-semibold tracking-tight text-white">{title}</h2>
          {subtitle ? <p className="mt-1 text-sm text-white/50">{subtitle}</p> : null}
        </div>
        {action ? <div className="shrink-0">{action}</div> : null}
      </div>
      <div className="p-6">{children}</div>
    </section>
  );
}

export function DashboardMetricCard({
  label,
  value,
  hint,
  tone = "blue",
  sparkline,
}: {
  label: string;
  value: string;
  hint?: string;
  tone?: "blue" | "green" | "orange" | "red" | "violet";
  sparkline?: number[];
}) {
  const toneClass = {
    blue: "from-[#2563eb]/28 to-[#60a5fa]/10 text-[#8cc4ff]",
    green: "from-[#10b981]/28 to-[#34d399]/10 text-[#6ee7b7]",
    orange: "from-[#f59e0b]/28 to-[#fbbf24]/10 text-[#fcd34d]",
    red: "from-[#ef4444]/28 to-[#fb7185]/10 text-[#fda4af]",
    violet: "from-[#7c3aed]/28 to-[#a78bfa]/10 text-[#c4b5fd]",
  }[tone];

  return (
    <div className="rounded-[18px] border border-white/8 bg-white/[0.03] p-5">
      <div className="text-sm text-white/55">{label}</div>
      <div className="mt-3 text-[30px] font-semibold leading-none text-white">{value}</div>
      {hint ? <div className="mt-3 text-sm text-white/45">{hint}</div> : null}
      {sparkline?.length ? (
        <div className={cn("mt-4 rounded-2xl border border-white/6 bg-gradient-to-r px-3 py-4", toneClass)}>
          <MiniSparkline values={sparkline} />
        </div>
      ) : null}
    </div>
  );
}

export function MiniSparkline({ values }: { values: number[] }) {
  const max = Math.max(...values, 1);
  const points = values
    .map((value, index) => {
      const x = (index / Math.max(values.length - 1, 1)) * 100;
      const y = 100 - (value / max) * 70 - 15;
      return `${x},${y}`;
    })
    .join(" ");

  return (
    <svg viewBox="0 0 100 100" className="h-14 w-full">
      <polyline fill="none" stroke="currentColor" strokeWidth="2.5" points={points} />
    </svg>
  );
}

export function LineChartPanel({
  values,
  labels,
  tone = "blue",
}: {
  values: number[];
  labels: string[];
  tone?: "blue" | "green" | "orange" | "red";
}) {
  const max = Math.max(...values, 1);
  const stroke = {
    blue: "#60a5fa",
    green: "#34d399",
    orange: "#fbbf24",
    red: "#fb7185",
  }[tone];
  const points = values
    .map((value, index) => {
      const x = (index / Math.max(values.length - 1, 1)) * 100;
      const y = 100 - (value / max) * 72 - 12;
      return `${x},${y}`;
    })
    .join(" ");

  return (
    <div className="rounded-[18px] border border-white/8 bg-[#0b1320] p-4">
      <svg viewBox="0 0 100 100" className="h-52 w-full">
        <polyline fill="none" stroke={stroke} strokeWidth="2.2" points={points} />
        {values.map((value, index) => {
          const x = (index / Math.max(values.length - 1, 1)) * 100;
          const y = 100 - (value / max) * 72 - 12;
          return <circle key={`${index}-${value}`} cx={x} cy={y} r="1.7" fill={stroke} />;
        })}
      </svg>
      <div className="mt-3 grid grid-cols-7 gap-2 text-center text-xs text-white/35">
        {labels.map((label) => (
          <div key={label}>{label}</div>
        ))}
      </div>
    </div>
  );
}

export function BarChartPanel({
  items,
  tone = "green",
}: {
  items: { label: string; value: number; note?: string }[];
  tone?: "green" | "blue" | "orange" | "red";
}) {
  const max = Math.max(...items.map((item) => item.value), 1);
  const barClass = {
    green: "from-[#10b981] to-[#34d399]",
    blue: "from-[#2563eb] to-[#60a5fa]",
    orange: "from-[#f59e0b] to-[#fbbf24]",
    red: "from-[#ef4444] to-[#fb7185]",
  }[tone];

  return (
    <div className="space-y-4">
      {items.map((item) => (
        <div key={item.label}>
          <div className="mb-2 flex items-center justify-between text-sm">
            <span className="text-white/70">{item.label}</span>
            <span className="font-medium text-white">{item.value}</span>
          </div>
          <div className="h-2.5 rounded-full bg-white/6">
            <div
              className={cn("h-2.5 rounded-full bg-gradient-to-r", barClass)}
              style={{ width: `${Math.max((item.value / max) * 100, 8)}%` }}
            />
          </div>
          {item.note ? <div className="mt-1 text-xs text-white/35">{item.note}</div> : null}
        </div>
      ))}
    </div>
  );
}

export function DonutChartPanel({
  items,
}: {
  items: { label: string; value: number; color: string }[];
}) {
  const total = items.reduce((sum, item) => sum + item.value, 0) || 1;
  let current = 0;

  return (
    <div className="grid gap-5 lg:grid-cols-[180px_1fr] lg:items-center">
      <div className="mx-auto h-44 w-44">
        <svg viewBox="0 0 42 42" className="h-full w-full -rotate-90">
          <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="rgba(255,255,255,0.06)" strokeWidth="4" />
          {items.map((item) => {
            const dash = (item.value / total) * 100;
            const dashArray = `${dash} ${100 - dash}`;
            const dashOffset = -current;
            current += dash;
            return (
              <circle
                key={item.label}
                cx="21"
                cy="21"
                r="15.915"
                fill="transparent"
                stroke={item.color}
                strokeWidth="4"
                strokeDasharray={dashArray}
                strokeDashoffset={dashOffset}
              />
            );
          })}
        </svg>
      </div>
      <div className="space-y-3">
        {items.map((item) => (
          <div key={item.label} className="flex items-center justify-between rounded-2xl border border-white/8 bg-white/[0.03] px-4 py-3">
            <div className="flex items-center gap-3">
              <span className="h-3 w-3 rounded-full" style={{ backgroundColor: item.color }} />
              <span className="text-sm text-white/70">{item.label}</span>
            </div>
            <span className="text-sm font-medium text-white">{item.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export function HeatmapPanel({
  values,
}: {
  values: { label: string; score: number }[];
}) {
  return (
    <div className="grid grid-cols-2 gap-3 xl:grid-cols-3">
      {values.map((item) => {
        const tone =
          item.score >= 80 ? "bg-[#10b981]/20 text-[#6ee7b7]" :
          item.score >= 60 ? "bg-[#2563eb]/18 text-[#93c5fd]" :
          item.score >= 40 ? "bg-[#f59e0b]/18 text-[#fcd34d]" :
          "bg-[#ef4444]/18 text-[#fda4af]";
        return (
          <div key={item.label} className={cn("rounded-[16px] border border-white/8 px-4 py-4", tone)}>
            <div className="text-xs uppercase tracking-[0.16em] opacity-75">{item.label}</div>
            <div className="mt-2 text-2xl font-semibold">{item.score}</div>
          </div>
        );
      })}
    </div>
  );
}
