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

export type AnalyzeResponse = {
  product: Product;
  analysis: AnalyzeResult;
  intelligence: ProductIntelligenceResult;
};

export type AnalyzeFullResponse =
  | {
      status: "OK";
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
    }
  | {
      status: "BLOCKED";
      lang: "zh" | "en";
      message: string;
    }
  | {
      product_score: "N/A";
      recommendation: "TRY_LATER";
      reason: "system_busy";
    };
