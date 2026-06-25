"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { getDashboardSummary } from "@/lib/api";
import type { DashboardStatCard, DashboardSummaryResponse } from "@/lib/types";
import { useDashboardStream } from "./use-dashboard-stream";

function animateNumber(from: number, to: number, onChange: (value: number) => void) {
  const start = performance.now();
  const duration = 420;
  let frame = 0;

  const tick = (now: number) => {
    const progress = Math.min((now - start) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    onChange(Math.round(from + (to - from) * eased));
    if (progress < 1) {
      frame = requestAnimationFrame(tick);
    }
  };

  frame = requestAnimationFrame(tick);
  return () => cancelAnimationFrame(frame);
}

export function useKpiRealtime(token: string, initialSummary: DashboardSummaryResponse, sourceCard: DashboardStatCard) {
  const [summary, setSummary] = useState(initialSummary);
  const [animatedValues, setAnimatedValues] = useState<Record<string, number>>(() =>
    Object.fromEntries(initialSummary.cards.filter((card) => typeof card.value === "number").map((card) => [card.key, Number(card.value)]))
  );
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const cleanupAnimationsRef = useRef<Array<() => void>>([]);

  const applySummary = useCallback((next: DashboardSummaryResponse) => {
    setSummary(next);
    cleanupAnimationsRef.current.forEach((fn) => fn());
    cleanupAnimationsRef.current = [];

    next.cards.forEach((card) => {
      if (typeof card.value !== "number") {
        return;
      }
      const from = animatedValues[card.key] ?? Number(card.value);
      const to = Number(card.value);
      if (from === to) {
        return;
      }
      const cleanup = animateNumber(from, to, (value) => {
        setAnimatedValues((current) => ({ ...current, [card.key]: value }));
      });
      cleanupAnimationsRef.current.push(cleanup);
    });
  }, [animatedValues]);

  const startPolling = useCallback(() => {
    if (pollingRef.current) {
      return;
    }
    pollingRef.current = setInterval(async () => {
      try {
        const next = await getDashboardSummary(token);
        applySummary(next);
      } catch {
        // 保留当前数据，不打断页面
      }
    }, 5000);
  }, [applySummary, token]);

  const stream = useDashboardStream({
    token,
    onSummary: (payload) => {
      applySummary(payload as DashboardSummaryResponse);
    },
    onPollingFallback: startPolling,
  });

  useEffect(() => {
    return () => {
      cleanupAnimationsRef.current.forEach((fn) => fn());
      cleanupAnimationsRef.current = [];
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
      }
    };
  }, []);

  const cards = useMemo(() => {
    const patched = summary.cards.map((card) =>
      typeof card.value === "number"
        ? {
            ...card,
            value: animatedValues[card.key] ?? Number(card.value),
          }
        : card
    );
    return [...patched, sourceCard];
  }, [animatedValues, sourceCard, summary.cards]);

  return {
    cards,
    summary,
    transport: stream.transport,
    connected: stream.connected,
  };
}
