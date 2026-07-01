"use client";

import { useMemo, useState } from "react";

import type { AdminRevenueResponse } from "@/lib/api/admin";

function money(cents: number) {
  return `¥ ${(cents / 100).toFixed(2)}`;
}

function formatDate(value: string) {
  return value.replace("T", " ").replace("Z", "");
}

export function AdminRevenueTableClient({ initialData }: { initialData: AdminRevenueResponse }) {
  const [userId, setUserId] = useState("");
  const [planFilter, setPlanFilter] = useState("");

  const filtered = useMemo(() => {
    return initialData.items.filter((item) => {
      if (userId && String(item.user_id || "") !== userId.trim()) return false;
      if (planFilter && item.member_type !== planFilter) return false;
      return true;
    });
  }, [initialData.items, planFilter, userId]);

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-3">
        <div className="border border-white/10 bg-[#101114] px-4 py-4">
          <div className="text-xs text-white/45">今日收入</div>
          <div className="mt-2 text-2xl font-semibold text-white">{money(initialData.summary.today_revenue_cents)}</div>
        </div>
        <div className="border border-white/10 bg-[#101114] px-4 py-4">
          <div className="text-xs text-white/45">本月收入</div>
          <div className="mt-2 text-2xl font-semibold text-white">{money(initialData.summary.month_revenue_cents)}</div>
        </div>
        <div className="border border-white/10 bg-[#101114] px-4 py-4">
          <div className="text-xs text-white/45">总收入</div>
          <div className="mt-2 text-2xl font-semibold text-white">{money(initialData.summary.total_revenue_cents)}</div>
        </div>
      </div>

      <div className="flex flex-wrap gap-3">
        <input
          value={userId}
          onChange={(event) => setUserId(event.target.value)}
          placeholder="筛选用户ID"
          className="h-10 w-[200px] rounded-md border border-white/10 bg-[#121316] px-3 text-sm text-white outline-none"
        />
        <select value={planFilter} onChange={(event) => setPlanFilter(event.target.value)} className="h-10 rounded-md border border-white/10 bg-[#121316] px-3 text-sm text-white outline-none">
          <option value="">全部会员</option>
          <option value="free">free</option>
          <option value="starter">plus</option>
          <option value="pro">pro</option>
          <option value="enterprise">enterprise</option>
        </select>
      </div>

      <div className="overflow-x-auto rounded-md border border-white/10">
        <table className="min-w-full border-collapse text-sm">
          <thead className="bg-[#111214] text-left text-white/55">
            <tr>
              <th className="border-b border-white/10 px-3 py-3 font-medium">order_id</th>
              <th className="border-b border-white/10 px-3 py-3 font-medium">user_id</th>
              <th className="border-b border-white/10 px-3 py-3 font-medium">会员类型</th>
              <th className="border-b border-white/10 px-3 py-3 font-medium">支付金额</th>
              <th className="border-b border-white/10 px-3 py-3 font-medium">支付方式</th>
              <th className="border-b border-white/10 px-3 py-3 font-medium">状态</th>
              <th className="border-b border-white/10 px-3 py-3 font-medium">时间</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((item) => (
              <tr key={item.order_id} className="border-b border-white/10 bg-[#0d0e10]">
                <td className="px-3 py-3">{item.order_id}</td>
                <td className="px-3 py-3">{item.user_id ?? "—"}</td>
                <td className="px-3 py-3">{item.member_type === "starter" ? "plus" : item.member_type}</td>
                <td className="px-3 py-3">{money(item.amount_cents)}</td>
                <td className="px-3 py-3">{item.payment_method || "未指定"}</td>
                <td className="px-3 py-3">{item.status}</td>
                <td className="px-3 py-3">{formatDate(item.updated_at)}</td>
              </tr>
            ))}
            {!filtered.length ? (
              <tr>
                <td colSpan={7} className="px-3 py-8 text-center text-white/45">没有匹配的收入记录</td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
    </div>
  );
}
