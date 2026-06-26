export type User = {
  id: number;
  email: string;
  full_name?: string | null;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
};

export type LoginResponse = {
  access_token: string;
  token_type: string;
  user: User;
};

export type CrawlResult = {
  product_id?: number | null;
  title: string;
  price: string;
  images: string[];
  rating: string;
  reviews: string;
  url: string;
};

export type PublicExtractResult =
  | {
      status: "OK";
      url: string;
      platform: "amazon" | "aliexpress" | "shopify";
      title: string;
      price: string;
      rating: string;
      review_count: string;
      images: string[];
      sales?: string | null;
      availability?: string | null;
      dom_parsed: boolean;
      entered_product_page: boolean;
    }
  | {
      status: "BLOCKED";
      reason: "captcha_or_login_or_invalid_page";
    };

export type AnalyzeResult = {
  title_zh: string;
  core_keywords: string[];
  selling_points: string[];
  sourcing_keywords: string[];
  source_links: {
    "1688_url": string;
    "pdd_url": string;
  };
};

export type ProductIntelligenceResult = {
  product_score: number;
  profit_estimate: string;
  competition_level: "low" | "medium" | "high";
  selling_potential: "weak" | "ok" | "strong";
  recommendation: "sell" | "monitor" | "ignore";
  reason: string[];
};

export type ProductIntelligenceEngineResponse = {
  market_score: number;
  competition_score: number;
  profit_score: number;
  risk_score: number;
  recommendation_score: number;
  recommendation: "推荐上架" | "观察" | "不推荐";
  reasons: string[];
};

export type MarketAnalyzeResponse = {
  trend_score: number;
  demand_score: number;
  competition_score: number;
  opportunity_score: number;
  recommendation_score: number;
  recommendation: string;
  reasons: string[];
  category?: string | null;
  source: string;
};

export type SupplierMatchItem = {
  product_id?: number | null;
  supplier_name?: string | null;
  platform: string;
  supplier_title: string;
  supplier_url: string;
  supplier_price?: number | null;
  currency?: string | null;
  match_score: number;
  availability: string;
};

export type SupplierMatchResponse = {
  suppliers: SupplierMatchItem[];
};

export type DecisionRecommendResponse = {
  intelligence_score: number;
  market_score: number;
  supplier_score: number;
  profit_score: number;
  risk_score: number;
  final_score: number;
  recommendation: string;
  recommendation_level: string;
  reasons: string[];
};

export type P5PredictionResponse = {
  product_id: number;
  keyword: string;
  forecast_window_days: number;
  growth_forecast: number;
  demand_forecast: number;
  competition_forecast: number;
  profit_forecast: number;
  explosion_probability: number;
  reasons: string[];
};

export type P5RecommendationItem = {
  product_id: number;
  title: string;
  title_zh?: string | null;
  keyword: string;
  category?: string | null;
  recommendation_score: number;
  estimated_profit: number;
  recommendation: string;
  reasons: string[];
};

export type P5RecommendationsResponse = {
  keyword?: string | null;
  category?: string | null;
  total_scanned: number;
  items: P5RecommendationItem[];
};

export type P5RankingEntry = {
  product_id: number;
  title: string;
  score: number;
  category?: string | null;
};

export type P5RankingsGroup = {
  top_10: P5RankingEntry[];
  top_50: P5RankingEntry[];
  top_100: P5RankingEntry[];
};

export type P5RankingsResponse = {
  scanned_products: number;
  profit_ranking: P5RankingsGroup;
  growth_ranking: P5RankingsGroup;
  risk_ranking: P5RankingsGroup;
};

export type ProductImage = {
  id: number;
  image_url: string;
  sort_order: number;
  is_primary: boolean;
};

export type Product = {
  id: number;
  platform_id: number;
  category_id?: number | null;
  external_product_id?: string | null;
  title: string;
  title_zh?: string | null;
  source_url: string;
  description_text?: string | null;
  currency_code?: string | null;
  current_price?: number | null;
  original_price?: number | null;
  review_count?: number;
  rating?: number | null;
  is_active: boolean;
  last_crawled_at?: string | null;
  created_at: string;
  updated_at: string;
  images: ProductImage[];
};

export type ProductListResponse = {
  items: Product[];
  total: number;
};

export type ProductBatchDeleteResponse = {
  ok: boolean;
  deleted_ids: number[];
};

export type AnalyzeResponse = {
  product: Product;
  analysis: AnalyzeResult;
  intelligence: ProductIntelligenceResult;
};

export type AnalyzeFullResponse =
  | {
      status: "OK" | "FALLBACK";
      lang: "zh" | "en";
      platform: "amazon" | "aliexpress" | "shopify";
      title: string;
      title_zh: string;
      price: string;
      image: string;
      score: number;
      product_score: number;
      recommendation: string;
      recommendation_key: "sell" | "monitor" | "ignore";
      profit_estimate: string;
      competition_level: string;
      competition_level_key: "low" | "medium" | "high";
      source_links: {
        "1688_url": string;
        "pdd_url": string;
      };
      core_keywords: string[];
      selling_points: string[];
      reason: string[];
      fallback_score?: number | null;
      ai_unavailable?: boolean;
    }
  | {
      status: "BLOCKED";
      lang: "zh" | "en";
      message: string;
    };

export type HealthResponse = {
  status: "ok" | "degraded" | "fail";
  version: string;
  env_status: {
    app_env: string;
    backend_url: boolean;
    frontend_url: boolean;
    frontend_origin: boolean;
    ws_url: boolean;
    next_public_api_base_url: boolean;
    next_public_ws_url: boolean;
  };
  services: {
    database: "ok" | "fail";
    ai: "ok" | "fail";
    crawler: "ok" | "fail";
  };
};

export type TaskStatusResponse = {
  success: boolean;
  status: "pending" | "running" | "success" | "error" | "blocked" | "unknown";
  message: string;
  detail: Record<string, unknown>;
  error_reason?: string | null;
  updated_at: string;
};

export type DashboardStatCard = {
  key: string;
  label: string;
  value: number | string;
  delta_text?: string | null;
  trend: "up" | "down" | "flat";
};

export type DashboardLatestProduct = {
  id: number;
  title: string;
  platform_name: string;
  price: string;
  category_name?: string | null;
  created_at: string;
};

export type DashboardCategorySnapshot = {
  name: string;
  product_count: number;
};

export type DashboardSummaryResponse = {
  cards: DashboardStatCard[];
  latest_products: DashboardLatestProduct[];
  top_categories: DashboardCategorySnapshot[];
  generated_at: string;
};

export type DashboardTrendPoint = {
  date: string;
  product_count: number;
};

export type DashboardTrendsResponse = {
  series: {
    period: string;
    points: DashboardTrendPoint[];
    peak_value: number;
  };
  generated_at: string;
};

export type DashboardTaskState = {
  key: string;
  label: string;
  status: "pending" | "running" | "success" | "error" | "blocked" | "unknown";
  message: string;
  error_reason?: string | null;
  updated_at: string;
};

export type DashboardRecentRun = {
  id: number;
  request_url: string;
  status: string;
  platform_name: string;
  crawled_at: string;
};

export type DashboardTasksResponse = {
  states: DashboardTaskState[];
  recent_runs: DashboardRecentRun[];
  generated_at: string;
};

export type DashboardSourceState = {
  platform_code: string;
  platform_name: string;
  health: "ok" | "warning" | "error";
  last_activity_text: string;
  product_count: number;
};

export type DashboardSourcesResponse = {
  sources: DashboardSourceState[];
  storage: {
    used_percent: number;
    total_products: number;
    total_runs: number;
  };
  generated_at: string;
};
