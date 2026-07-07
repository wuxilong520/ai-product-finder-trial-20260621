import type { CurrentBillingStatus } from "@/lib/api/billing";

export function PlanAccessPanel({
  currentPlan,
  title = "当前套餐权限",
  compact = false,
}: {
  currentPlan: CurrentBillingStatus | null;
  title?: string;
  compact?: boolean;
}) {
  if (!currentPlan) {
    return (
      <div className="rounded-2xl border border-white/8 bg-white/5 p-4 text-sm text-white/65">
        当前还没有登录工作区，所以这里只展示公开内容。登录后会直接看到你的套餐、可用模型和权限范围。
      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-white/8 bg-white/5 p-4 text-sm text-white/75">
      <div className="text-xs text-white/45">{title}</div>
      <div className="mt-2 flex flex-wrap items-center gap-2">
        <span className="rounded-full border border-[#4F7CFF]/20 bg-[#4F7CFF]/10 px-3 py-1 text-xs text-[#D8E3FF]">
          套餐：{currentPlan.plan_name}
        </span>
        <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-white/70">
          状态：{currentPlan.status}
        </span>
        {currentPlan.supports_custom_model ? (
          <span className="rounded-full border border-[#3DD68C]/20 bg-[#3DD68C]/10 px-3 py-1 text-xs text-[#D4FFEC]">
            支持企业专属模型
          </span>
        ) : null}
      </div>
      <div className="mt-3">
        <div className="text-xs text-white/45">可用模型</div>
        <div className="mt-1 text-white">{currentPlan.allowed_ai_models.join(" / ") || "未开放"}</div>
      </div>
      {!compact ? (
        <div className="mt-3">
          <div className="text-xs text-white/45">可用 AI 通道</div>
          <div className="mt-1 text-white">{currentPlan.allowed_ai_providers.join(" / ") || "未开放"}</div>
        </div>
      ) : null}
      <div className="mt-3 text-white/60">{currentPlan.ai_policy_note || "当前套餐权限会直接影响你能调用的 AI 模型。"}</div>
    </div>
  );
}
