import type {
  DashboardSourcesResponse,
  DashboardSummaryResponse,
  DashboardTasksResponse,
  DashboardTrendsResponse,
} from "@/lib/types";

export const EMPTY_DASHBOARD_SUMMARY: DashboardSummaryResponse = {
  cards: [],
  latest_products: [],
  top_categories: [],
  generated_at: "",
};

export const EMPTY_DASHBOARD_TRENDS: DashboardTrendsResponse = {
  series: {
    period: "7d",
    points: [],
    peak_value: 0,
  },
  generated_at: "",
};

export const EMPTY_DASHBOARD_TASKS: DashboardTasksResponse = {
  states: [],
  recent_runs: [],
  generated_at: "",
};

export const EMPTY_DASHBOARD_SOURCES: DashboardSourcesResponse = {
  sources: [],
  storage: {
    used_percent: 0,
    total_products: 0,
    total_runs: 0,
  },
  generated_at: "",
};

export async function safeLoad<T>(loader: () => Promise<T>, fallback: T): Promise<T> {
  try {
    return await loader();
  } catch {
    return fallback;
  }
}
