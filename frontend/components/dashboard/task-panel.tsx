"use client";

import { CheckCircle2, Clock3, PauseCircle, XCircle } from "lucide-react";

import { Card } from "@/design-system/components";
import { useTaskStream } from "@/components/dashboard/realtime/use-task-stream";
import { Language, t } from "@/lib/i18n";
import type { DashboardSourcesResponse, DashboardTasksResponse } from "@/lib/types";

function formatTime(value: string) {
  return new Intl.DateTimeFormat("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

function formatTaskName(requestUrl: string, platformName: string) {
  try {
    const host = new URL(requestUrl).hostname.replace("www.", "");
    return `${platformName} · ${host}`;
  } catch {
    return platformName || "";
  }
}

function toStatusTone(status: string) {
  if (status === "success") return "text-emerald-300";
  if (status === "running") return "text-cyan-300";
  if (status === "blocked") return "text-white/60";
  return "text-rose-300";
}

export function TaskPanel({
  token,
  initialTasks,
  initialSources,
  lang,
}: {
  token: string;
  initialTasks: DashboardTasksResponse;
  initialSources: DashboardSourcesResponse;
  lang: Language;
}) {
  const text = t(lang);
  const live = useTaskStream(token, initialTasks);
  const tasks = live.tasks;
  const recentTasks = tasks.recent_runs.slice(0, 6);
  const totalTaskCount = tasks.recent_runs.length;
  const successTaskCount = tasks.recent_runs.filter((item) => item.status === "success").length;
  const errorTaskCount = tasks.recent_runs.filter((item) => item.status === "failed" || item.status === "error").length;
  const runningTaskCount = tasks.recent_runs.filter((item) => item.status === "running").length;
  const blockedTaskCount = tasks.recent_runs.filter((item) => item.status === "blocked").length;

  return (
    <div className="space-y-5">
      <Card className="rounded-[34px] border border-white/8 bg-[#121c2c] p-8 shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
        <div className="mb-6">
          <div className="text-[18px] font-semibold">{text.taskPanelTitle}</div>
          <div className="mt-2 text-sm text-white/45">{text.taskPanelDesc}</div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <MiniStatusCard icon={<Clock3 className="h-4 w-4" />} label={text.taskRunning} value={runningTaskCount} tone="text-cyan-300" />
          <MiniStatusCard icon={<CheckCircle2 className="h-4 w-4" />} label={text.taskSuccess} value={successTaskCount} tone="text-emerald-300" />
          <MiniStatusCard icon={<XCircle className="h-4 w-4" />} label={text.taskFailed} value={errorTaskCount} tone="text-rose-300" />
          <MiniStatusCard icon={<PauseCircle className="h-4 w-4" />} label={text.taskPaused} value={blockedTaskCount} tone="text-white/65" />
        </div>

        <div className="mt-6 rounded-[24px] border border-white/8 bg-white/[0.03] px-5 py-4">
          <div className="text-sm text-white/45">{text.taskTotal}</div>
          <div className="mt-2 text-[34px] font-semibold leading-none text-white">{totalTaskCount}</div>
        </div>
      </Card>

      <Card className="rounded-[34px] border border-white/8 bg-[#121c2c] p-8 shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
        <div className="mb-5 flex items-center justify-between">
          <div>
            <div className="text-[18px] font-semibold">{text.taskRecentTitle}</div>
            <div className="mt-2 text-sm text-white/45">{text.taskRecentDesc}</div>
          </div>
          <div className="text-sm text-[#60a5fa]">{live.transport === "sse" ? text.taskRealtime : text.taskAutoRefresh}</div>
        </div>

        <div className="space-y-3">
          {recentTasks.length ? (
            recentTasks.map((item) => (
              <div key={item.id} className="rounded-[24px] border border-white/8 bg-white/[0.03] px-5 py-4">
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <div className="truncate text-[15px] font-medium text-white">{formatTaskName(item.request_url, item.platform_name)}</div>
                    <div className="mt-1.5 text-[13px] text-white/45">{formatTime(item.crawled_at)}</div>
                  </div>
                  <div className={`shrink-0 text-[14px] font-medium ${toStatusTone(item.status)}`}>
                    {item.status === "success" ? text.taskSuccess : item.status === "running" ? text.taskRunning : item.status === "blocked" ? text.taskPaused : text.taskFailed}
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="rounded-[24px] border border-dashed border-white/10 bg-white/[0.02] px-5 py-10 text-center text-sm text-white/35">
              {text.taskNoRecords}
            </div>
          )}
        </div>
      </Card>

      <Card className="rounded-[34px] border border-white/8 bg-[#121c2c] p-8 shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
        <div className="mb-5 flex items-center justify-between">
          <div className="text-[18px] font-semibold">{text.sourceOverviewTitle}</div>
          <div className="text-sm text-white/45">{text.sourceOverviewDesc}</div>
        </div>
        <div className="space-y-4">
          {initialSources.sources.map((source) => (
            <div key={source.platform_code} className="flex items-center justify-between rounded-[24px] border border-white/8 bg-white/[0.03] px-5 py-4">
              <div>
                <div className="text-[15px] font-medium text-white">{source.platform_name}</div>
                <div className="mt-1.5 text-[13px] text-white/45">{source.last_activity_text}</div>
              </div>
              <div className="text-right">
                <div className={source.health === "ok" ? "text-[15px] text-emerald-300" : source.health === "warning" ? "text-[15px] text-amber-300" : "text-[15px] text-rose-300"}>
                  {source.health === "ok" ? text.sourceHealthOk : source.health === "warning" ? text.sourceHealthWarning : text.sourceHealthError}
                </div>
                <div className="mt-1.5 text-[13px] text-white/45">{source.product_count} {text.productsUnit}</div>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}

function MiniStatusCard({
  icon,
  label,
  value,
  tone,
}: {
  icon: React.ReactNode;
  label: string;
  value: number;
  tone: string;
}) {
  return (
    <div className="rounded-[24px] border border-white/8 bg-white/[0.03] px-4 py-4">
      <div className={`flex items-center gap-2 text-sm ${tone}`}>
        {icon}
        <span>{label}</span>
      </div>
      <div className="mt-3 text-[26px] font-semibold leading-none text-white">{value}</div>
    </div>
  );
}
