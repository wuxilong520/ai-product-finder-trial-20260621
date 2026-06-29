"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { getDashboardTasks } from "@/lib/api-gateway";
import type { DashboardTaskState, DashboardTasksResponse, TaskStatusResponse } from "@/lib/types";
import { useDashboardStream } from "./use-dashboard-stream";

function patchTaskStates(current: DashboardTaskState[], taskName: string, payload: TaskStatusResponse) {
  const nextState: DashboardTaskState = {
    key: taskName,
    label: current.find((item) => item.key === taskName)?.label || taskName,
    status: payload.status,
    message: payload.message,
    error_reason: payload.error_reason || null,
    updated_at: payload.updated_at,
  };

  const index = current.findIndex((item) => item.key === taskName);
  if (index === -1) {
    return [nextState, ...current];
  }

  return current.map((item, itemIndex) => (itemIndex === index ? nextState : item));
}

export function useTaskStream(token: string, initialTasks: DashboardTasksResponse) {
  const [tasks, setTasks] = useState(initialTasks);
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const taskNames = useMemo(() => {
    const names = initialTasks.states.map((item) => item.key).filter(Boolean);
    return names.length ? names : ["crawl", "analyze"];
  }, [initialTasks.states]);

  const applyTasks = useCallback((next: DashboardTasksResponse) => {
    setTasks(next);
  }, []);

  const startPolling = useCallback(() => {
    if (pollingRef.current) {
      return;
    }
    pollingRef.current = setInterval(async () => {
      try {
        const next = await getDashboardTasks(token);
        applyTasks(next);
      } catch {
        // 保留当前任务状态
      }
    }, 5000);
  }, [applyTasks, token]);

  const stream = useDashboardStream({
    token,
    taskNames,
    onTasks: (payload) => {
      applyTasks(payload as DashboardTasksResponse);
    },
    onTaskState: (taskName, payload) => {
      const next = payload as TaskStatusResponse;
      setTasks((current) => ({
        ...current,
        states: patchTaskStates(current.states, taskName, next),
      }));
    },
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
    tasks,
    transport: stream.transport,
    connected: stream.connected,
  };
}
