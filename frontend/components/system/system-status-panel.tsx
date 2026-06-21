"use client";

import { useEffect, useState } from "react";

import { Badge, Card, StatusAlert, StatusSummary } from "@/design-system/components";
import { getApiBaseUrl, getSystemHealth, getWsBaseUrl } from "@/lib/api";
import { Language } from "@/lib/i18n";
import { HealthResponse } from "@/lib/types";

function toUiStatus(value: string): "running" | "success" | "error" | "warning" | "blocked" {
  if (value === "ok" || value === "success") return "success";
  if (value === "degraded") return "warning";
  if (value === "fail" || value === "error") return "error";
  if (value === "blocked") return "blocked";
  return "running";
}

export function SystemStatusPanel({ lang }: { lang: Language }) {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    getSystemHealth()
      .then((result) => {
        if (!cancelled) {
          setHealth(result);
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "系统状态读取失败");
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const title = lang === "zh" ? "系统状态面板" : "System Status";
  const apiLabel = lang === "zh" ? "API 地址" : "API URL";
  const wsLabel = lang === "zh" ? "WS 地址" : "WS URL";
  const envLabel = lang === "zh" ? "运行环境" : "Environment";
  const dbLabel = lang === "zh" ? "数据库" : "Database";
  const aiLabel = lang === "zh" ? "AI 服务" : "AI service";
  const crawlerLabel = lang === "zh" ? "采集器" : "Crawler";
  const envCheckLabel = lang === "zh" ? "环境变量" : "Env check";

  return (
    <Card className="p-5">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-sm text-app-text-muted">{title}</p>
          <h3 className="mt-2 text-xl font-semibold text-white">{health?.status || (lang === "zh" ? "读取中" : "Loading")}</h3>
        </div>
        <Badge variant={toUiStatus(health?.status || "running")} dot>
          {health?.version || "v2"}
        </Badge>
      </div>

      <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        <StatusSummary label={envLabel} value={health?.env_status.app_env || "—"} status={toUiStatus(health?.status || "running")} />
        <StatusSummary label={apiLabel} value={getApiBaseUrl() || "未配置"} status={getApiBaseUrl() ? "success" : "error"} />
        <StatusSummary label={wsLabel} value={getWsBaseUrl() || "未配置"} status={getWsBaseUrl() ? "success" : "warning"} />
        <StatusSummary label={dbLabel} value={health?.services.database || "—"} status={toUiStatus(health?.services.database || "running")} />
        <StatusSummary label={aiLabel} value={health?.services.ai || "—"} status={toUiStatus(health?.services.ai || "running")} />
        <StatusSummary label={crawlerLabel} value={health?.services.crawler || "—"} status={toUiStatus(health?.services.crawler || "running")} />
      </div>

      <div className="mt-4">
        <StatusSummary
          label={envCheckLabel}
          value={
            health
              ? Object.entries(health.env_status)
                  .filter(([key]) => key !== "app_env")
                  .every(([, value]) => Boolean(value))
                ? (lang === "zh" ? "已配置" : "Configured")
                : (lang === "zh" ? "有缺失" : "Missing items")
              : "—"
          }
          status={
            health
              ? Object.entries(health.env_status)
                  .filter(([key]) => key !== "app_env")
                  .every(([, value]) => Boolean(value))
                ? "success"
                : "error"
              : "running"
          }
        />
      </div>

      {error ? <div className="mt-4"><StatusAlert status="error" message={error} /></div> : null}
    </Card>
  );
}
