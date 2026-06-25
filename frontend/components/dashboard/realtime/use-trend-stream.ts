"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { getDashboardSources, getDashboardTrends } from "@/lib/api";
import type { DashboardSourcesResponse, DashboardTrendsResponse } from "@/lib/types";
import { useDashboardStream } from "./use-dashboard-stream";

export function useTrendStream(token: string, initialTrends: DashboardTrendsResponse, initialSources: DashboardSourcesResponse) {
  const [trends, setTrends] = useState(initialTrends);
  const [sources, setSources] = useState(initialSources);
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const refreshTrendAndSources = useCallback(async () => {
    try {
      const [nextTrends, nextSources] = await Promise.all([
        getDashboardTrends(token),
        getDashboardSources(token),
      ]);

      setTrends((current) => ({
        ...nextTrends,
        series: {
          ...nextTrends.series,
          points: nextTrends.series.points.map((point, index) => current.series.points[index] ?? point).map((existingOrPoint, index) => {
            const latest = nextTrends.series.points[index];
            return latest ? { ...existingOrPoint, ...latest } : existingOrPoint;
          }),
        },
      }));
      setSources(nextSources);
    } catch {
      // 刷新失败时保留当前数据
    }
  }, [token]);

  const startPolling = useCallback(() => {
    if (pollingRef.current) {
      return;
    }
    pollingRef.current = setInterval(refreshTrendAndSources, 30000);
  }, [refreshTrendAndSources]);

  const stream = useDashboardStream({
    token,
    onSummary: refreshTrendAndSources,
    onTasks: refreshTrendAndSources,
    onPollingFallback: startPolling,
  });

  useEffect(() => {
    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
      }
    };
  }, []);

  return {
    trends,
    sources,
    transport: stream.transport,
    connected: stream.connected,
  };
}
