import type { LucideIcon } from "lucide-react";
import { BarChart3, Boxes, ClipboardList, LayoutGrid, Rocket, ShieldCheck, Sparkles, TrendingUp } from "lucide-react";

export const BRAND_NAME = "商航AI";
export const BRAND_TAGLINE = "全球跨境商品智能决策平台";

export const BUSINESS_TERMS = {
  market_score: "市场机会指数",
  supplier_score: "供应稳定性",
  profit_score: "利润空间预测",
  recommendation: "AI进入建议",
  procurement_pool: "智能采购方案",
  supplier_intelligence: "供应链竞争中心",
  commercial_score: "商业判断指数",
} as const;

export type HallCard = {
  title: string;
  description: string;
  badge: string;
  metric: string;
  tone: "blue" | "emerald" | "amber" | "rose";
  icon: LucideIcon;
};

export const homeHallCards: HallCard[] = [
  {
    title: "市场趋势大厅",
    description: "用榜单和趋势判断机会方向，不先看后台字段。",
    badge: "发现机会",
    metric: "市场机会指数",
    tone: "blue",
    icon: TrendingUp,
  },
  {
    title: "商品机会榜",
    description: "把可做商品按机会强弱排开，先看最值得深入的项。",
    badge: "推荐商品",
    metric: "机会评分",
    tone: "emerald",
    icon: LayoutGrid,
  },
  {
    title: "利润预测区",
    description: "统一看利润空间、成本带和放量弹性，减少拍脑袋。",
    badge: "预测利润",
    metric: "利润空间预测",
    tone: "amber",
    icon: Sparkles,
  },
  {
    title: "供应链方案",
    description: "把供应稳定性、MOQ、价格和风险一起看。",
    badge: "供应方案",
    metric: "供应稳定性",
    tone: "rose",
    icon: Boxes,
  },
];

export const topNavCopy = [
  { label: "首页", href: "/" },
  { label: "市场分析", href: "/insights" },
  { label: "商业机会", href: "/dashboard/opportunity" },
  { label: "采购方案", href: "/action-center/procurement" },
  { label: "AI分析", href: "/tasks" },
  { label: "设置", href: "/settings" },
] as const;

export const userPathCopy = [
  {
    title: "发现机会",
    desc: "先从趋势和榜单里挑出值得看的商品方向。",
    icon: TrendingUp,
  },
  {
    title: "分析商品",
    desc: "进入商品详情，看 AI 商业报告怎么判断。",
    icon: ClipboardList,
  },
  {
    title: "预测利润",
    desc: "把成本、利润空间和风险放在一张卡里看。",
    icon: BarChart3,
  },
  {
    title: "制定采购方案",
    desc: "进入供应链竞争中心，选更稳的供应商方案。",
    icon: ShieldCheck,
  },
  {
    title: "执行上架",
    desc: "把判断转成下一步动作，而不是停在看数据。",
    icon: Rocket,
  },
] as const;
