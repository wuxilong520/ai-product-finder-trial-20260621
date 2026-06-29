"use client";

import { useEffect, useMemo, useRef, useState } from "react";

import { getApiRootUrl, getApiV1BaseUrl, getWsBaseUrl } from "@/lib/api-gateway";

export type DashboardRealtimeTransport = "sse" | "websocket" | "polling" | "idle";

type DashboardStreamOptions = {
  token: string;
  taskNames?: string[];
  onSummary?: (payload: unknown) => void;
  onTasks?: (payload: unknown) => void;
  onTaskState?: (taskName: string, payload: unknown) => void;
  onSseFallback?: () => void;
  onPollingFallback?: () => void;
};

export function useDashboardStream({
  token,
  taskNames = [],
  onSummary,
  onTasks,
  onTaskState,
  onSseFallback,
  onPollingFallback,
}: DashboardStreamOptions) {
  const [transport, setTransport] = useState<DashboardRealtimeTransport>("idle");
  const [connected, setConnected] = useState(false);
  const wsStartedRef = useRef(false);

  const streamUrl = useMemo(() => {
    const base = getApiV1BaseUrl();
    return `${base}/stream/dashboard?token=${encodeURIComponent(token)}`;
  }, [token]);

  const wsBase = useMemo(() => {
    const configured = getWsBaseUrl();
    if (configured) {
      return configured;
    }
    const apiRoot = getApiRootUrl();
    if (!apiRoot) {
      return "";
    }
    if (apiRoot.startsWith("https://")) {
      return apiRoot.replace(/^https:\/\//, "wss://") + "/ws";
    }
    if (apiRoot.startsWith("http://")) {
      return apiRoot.replace(/^http:\/\//, "ws://") + "/ws";
    }
    return "";
  }, []);

  useEffect(() => {
    if (!token) {
      return;
    }

    let closed = false;
    let source: EventSource | null = null;
    let sockets: WebSocket[] = [];

    const startWebSockets = () => {
      if (wsStartedRef.current || !taskNames.length) {
        return false;
      }
      wsStartedRef.current = true;

      try {
        sockets = taskNames.map((taskName) => {
          const socket = new WebSocket(`${wsBase}/${taskName}`);
          socket.onopen = () => {
            if (!closed) {
              setTransport("websocket");
              setConnected(true);
            }
          };
          socket.onmessage = (event) => {
            if (closed) {
              return;
            }
            try {
              const payload = JSON.parse(event.data);
              onTaskState?.(taskName, payload);
            } catch {
              // 忽略格式异常消息，避免打断当前页面
            }
          };
          socket.onerror = () => {
            if (!closed) {
              onPollingFallback?.();
              setTransport("polling");
              setConnected(true);
            }
          };
          socket.onclose = () => {
            if (!closed) {
              onPollingFallback?.();
              setTransport("polling");
              setConnected(true);
            }
          };
          return socket;
        });
        return true;
      } catch {
        return false;
      }
    };

    try {
      source = new EventSource(streamUrl);
      setTransport("sse");
      setConnected(true);

      source.addEventListener("summary", (event) => {
        if (closed) return;
        try {
          onSummary?.(JSON.parse(event.data));
        } catch {
          // 忽略无效 SSE 数据
        }
      });

      source.addEventListener("tasks", (event) => {
        if (closed) return;
        try {
          onTasks?.(JSON.parse(event.data));
        } catch {
          // 忽略无效 SSE 数据
        }
      });

      source.onerror = () => {
        source?.close();
        if (closed) {
          return;
        }
        onSseFallback?.();
        const wsStarted = startWebSockets();
        if (!wsStarted) {
          onPollingFallback?.();
          setTransport("polling");
          setConnected(true);
        }
      };
    } catch {
      const wsStarted = startWebSockets();
      if (!wsStarted) {
        onPollingFallback?.();
        setTransport("polling");
        setConnected(true);
      }
    }

    return () => {
      closed = true;
      wsStartedRef.current = false;
      source?.close();
      sockets.forEach((socket) => socket.close());
      sockets = [];
    };
  }, [onPollingFallback, onSseFallback, onSummary, onTaskState, onTasks, streamUrl, taskNames, token, wsBase]);

  return {
    transport,
    connected,
  };
}
