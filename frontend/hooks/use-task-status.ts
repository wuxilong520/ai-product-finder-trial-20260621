"use client";

import { useEffect, useRef, useState } from "react";

import { getTaskStatus, getWsBaseUrl } from "@/lib/api-gateway";
import { TaskStatusResponse } from "@/lib/types";

const defaultState: TaskStatusResponse = {
  success: true,
  status: "pending",
  message: "等待任务开始",
  detail: {},
  error_reason: null,
  updated_at: "",
};

export function useTaskStatus(taskName: "crawl" | "analyze") {
  const [state, setState] = useState<TaskStatusResponse>(defaultState);
  const [transport, setTransport] = useState<"ws" | "polling" | "idle">("idle");
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    let socket: WebSocket | null = null;
    let cancelled = false;

    async function readOnce() {
      try {
        const result = await getTaskStatus(taskName);
        if (!cancelled) {
          setState(result);
        }
      } catch {
        if (!cancelled) {
          setState((current) => ({
            ...current,
            status: "error",
            message: "状态读取失败",
          }));
        }
      }
    }

    function startPolling() {
      setTransport("polling");
      readOnce();
      pollingRef.current = setInterval(readOnce, 3000);
    }

    try {
      const wsBase = getWsBaseUrl();
      if (!wsBase) {
        startPolling();
        return;
      }

      socket = new WebSocket(`${wsBase}/${taskName}`);
      socket.onopen = () => {
        setTransport("ws");
      };
      socket.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data) as TaskStatusResponse;
          setState(payload);
        } catch {
          setState((current) => ({
            ...current,
            status: "error",
            message: "状态消息解析失败",
          }));
        }
      };
      socket.onerror = () => {
        if (!pollingRef.current) {
          startPolling();
        }
      };
      socket.onclose = () => {
        if (!pollingRef.current) {
          startPolling();
        }
      };
    } catch {
      startPolling();
    }

    return () => {
      cancelled = true;
      if (socket) {
        socket.close();
      }
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
        pollingRef.current = null;
      }
    };
  }, [taskName]);

  return {
    state,
    transport,
  };
}
