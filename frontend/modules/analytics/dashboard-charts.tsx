"use client";

import { Card } from "@/design-system/components";
import { Language, t } from "@/lib/i18n";
import type { DashboardCategorySnapshot, DashboardTrendPoint } from "@/lib/types";

function formatShortDate(date: string) {
  return date.slice(5);
}

export function TrendChartCard({ points, lang }: { points: DashboardTrendPoint[]; lang: Language }) {
  const text = t(lang);
  const maxValue = Math.max(...points.map((point) => point.product_count), 1);
  const hasData = points.some((point) => point.product_count > 0);
  const chartPoints = points
    .map((point, index) => {
      const x = (index / Math.max(points.length - 1, 1)) * 100;
      const y = 100 - (point.product_count / maxValue) * 80 - 10;
      return `${x},${y}`;
    })
    .join(" ");

  return (
    <Card className="rounded-[28px] border border-white/8 bg-[#121c2c] p-6 shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <div className="text-xl font-semibold text-white">{text.chartTrendTitle}</div>
          <div className="mt-1 text-sm text-white/45">{text.chartTrendDesc}</div>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-2 text-sm text-white/70">{text.chartLast7Days}</div>
      </div>
      <div className="rounded-[24px] border border-white/6 bg-[linear-gradient(180deg,rgba(12,22,38,0.94),rgba(10,17,29,0.9))] p-4">
        <svg viewBox="0 0 100 100" className="h-64 w-full">
          <defs>
            <linearGradient id="trend-fill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="rgba(37,99,235,0.4)" />
              <stop offset="100%" stopColor="rgba(37,99,235,0.02)" />
            </linearGradient>
          </defs>
          <polyline
            fill="none"
            stroke="rgba(59,130,246,0.95)"
            strokeWidth="2"
            points={chartPoints}
          />
          <polyline
            fill="url(#trend-fill)"
            stroke="none"
            points={`0,100 ${chartPoints} 100,100`}
          />
          {points.map((point, index) => {
            const x = (index / Math.max(points.length - 1, 1)) * 100;
            const y = 100 - (point.product_count / maxValue) * 80 - 10;
            return <circle key={`${point.date}-${index}`} cx={x} cy={y} r="1.8" fill="#3b82f6" />;
          })}
        </svg>
        {!hasData ? (
          <div className="-mt-36 flex h-36 items-center justify-center text-sm text-white/35">
            {text.chartNoTrend}
          </div>
        ) : null}
        <div className="mt-4 grid grid-cols-7 gap-2 text-center text-xs text-white/45">
          {points.map((point) => (
            <div key={point.date}>{formatShortDate(point.date)}</div>
          ))}
        </div>
      </div>
    </Card>
  );
}

export function TopCategoriesCard({ categories, lang }: { categories: DashboardCategorySnapshot[]; lang: Language }) {
  const text = t(lang);
  return (
    <Card className="rounded-[28px] border border-white/8 bg-[#121c2c] p-6 shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
      <div className="mb-5 flex items-center justify-between">
        <div>
          <div className="text-xl font-semibold text-white">{text.chartTopCategoryTitle}</div>
          <div className="mt-1 text-sm text-white/45">{text.chartTopCategoryDesc}</div>
        </div>
        <div className="text-sm text-[#60a5fa]">{text.chartViewAll}</div>
      </div>
      {categories.length ? (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {categories.map((item) => (
            <div key={item.name} className="rounded-[22px] border border-white/8 bg-white/[0.03] px-4 py-5">
              <div className="text-sm text-white/60">{item.name}</div>
              <div className="mt-4 text-2xl font-semibold text-white">{item.product_count.toLocaleString()}</div>
            </div>
          ))}
        </div>
      ) : (
        <div className="rounded-[22px] border border-dashed border-white/10 bg-white/[0.02] px-5 py-10 text-center text-sm text-white/35">
          {text.chartNoCategory}
        </div>
      )}
    </Card>
  );
}
