"use client";

import { useEffect, useMemo, useState } from "react";

import { getApiV1BaseUrl, getDashboardSummary, getDashboardTasks } from "@/lib/api-gateway";
import type { DashboardSummaryResponse, DashboardTasksResponse } from "@/lib/types";

type LiveState = {
  summary: DashboardSummaryResponse | null;
  tasks: DashboardTasksResponse | null;
  transport: "sse" | "polling" | "idle";
  connected: boolean;
};

export function useDashboardLive(token: string, initialSummary: DashboardSummaryResponse, initialTasks: DashboardTasksResponse) {
  const [state, setState] = useState<LiveState>({
    summary: initialSummary,
    tasks: initialTasks,
    transport: "idle",
    connected: false,
  });

  const streamUrl = useMemo(() => {
    const base = getApiV1BaseUrl();
    return `${base}/stream/dashboard?token=${encodeURIComponent(token)}`;
  }, [token]);

  useEffect(() => {
    if (!token) {
      return;
    }

    let closed = false;
    let pollingTimer: ReturnType<typeof setInterval> | null = null;
    let source: EventSource | null = null;

    const startPolling = () => {
      if (pollingTimer) {
        return;
      }
      setState((current) => ({
        ...current,
        transport: "polling",
        connected: true,
      }));
      pollingTimer = setInterval(async () => {
        try {
          const [summary, tasks] = await Promise.all([
            getDashboardSummary(token),
            getDashboardTasks(token),
          ]);
          if (!closed) {
            setState({
              summary,
              tasks,
              transport: "polling",
              connected: true,
            });
          }
        } catch {
          // polling 失败时保留旧数据，不让页面崩
        }
      }, 5000);
    };

    try {
      source = new EventSource(streamUrl);
      setState((current) => ({
        ...current,
        transport: "sse",
        connected: true,
      }));

      source.addEventListener("summary", (event) => {
        const next = JSON.parse(event.data) as DashboardSummaryResponse;
        setState((current) => ({ ...current, summary: next, transport: "sse", connected: true }));
      });

      source.addEventListener("tasks", (event) => {
        const next = JSON.parse(event.data) as DashboardTasksResponse;
        setState((current) => ({ ...current, tasks: next, transport: "sse", connected: true }));
      });

      source.onerror = () => {
        source?.close();
        startPolling();
      };
    } catch {
      startPolling();
    }

    return () => {
      closed = true;
      source?.close();
      if (pollingTimer) {
        clearInterval(pollingTimer);
      }
    };
  }, [streamUrl, token]);

  return state;
}
