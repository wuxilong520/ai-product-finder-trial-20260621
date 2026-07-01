"use client";

import { useMemo, useState } from "react";

import {
  banAdminUser,
  changeAdminUserMembership,
  type AdminUserRow,
  resetAdminUserApiKey,
  unbanAdminUser,
} from "@/lib/api/admin";

function formatDate(value?: string | null) {
  if (!value) return "—";
  return value.replace("T", " ").replace("Z", "");
}

export function AdminUsersTableClient({
  initialItems,
  token,
}: {
  initialItems: AdminUserRow[];
  token: string;
}) {
  const [items, setItems] = useState(initialItems);
  const [search, setSearch] = useState("");
  const [planFilter, setPlanFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [busyUserId, setBusyUserId] = useState<number | null>(null);
  const [message, setMessage] = useState("");

  const filtered = useMemo(() => {
    return items.filter((item) => {
      if (search) {
        const key = search.trim().toLowerCase();
        if (!String(item.user_id).includes(key) && !(item.contact || "").toLowerCase().includes(key)) {
          return false;
        }
      }
      if (planFilter && item.member_level !== planFilter) return false;
      if (statusFilter && item.status !== statusFilter) return false;
      return true;
    });
  }, [items, planFilter, search, statusFilter]);

  async function runAction(userId: number, action: () => Promise<unknown>, successText: string, patch: Partial<AdminUserRow>) {
    try {
      setBusyUserId(userId);
      setMessage("");
      await action();
      setItems((current) => current.map((item) => (item.user_id === userId ? { ...item, ...patch } : item)));
      setMessage(successText);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "操作失败");
    } finally {
      setBusyUserId(null);
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-3">
        <input
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder="搜索 user_id / 邮箱"
          className="h-10 w-[260px] rounded-md border border-white/10 bg-[#121316] px-3 text-sm text-white outline-none"
        />
        <select value={planFilter} onChange={(event) => setPlanFilter(event.target.value)} className="h-10 rounded-md border border-white/10 bg-[#121316] px-3 text-sm text-white outline-none">
          <option value="">全部会员</option>
          <option value="free">free</option>
          <option value="starter">plus</option>
          <option value="pro">pro</option>
          <option value="enterprise">enterprise</option>
        </select>
        <select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)} className="h-10 rounded-md border border-white/10 bg-[#121316] px-3 text-sm text-white outline-none">
          <option value="">全部状态</option>
          <option value="active">active</option>
          <option value="banned">banned</option>
        </select>
      </div>

      {message ? <div className="text-sm text-white/70">{message}</div> : null}

      <div className="overflow-x-auto rounded-md border border-white/10">
        <table className="min-w-full border-collapse text-sm">
          <thead className="bg-[#111214] text-left text-white/55">
            <tr>
              <th className="border-b border-white/10 px-3 py-3 font-medium">user_id</th>
              <th className="border-b border-white/10 px-3 py-3 font-medium">手机号/邮箱</th>
              <th className="border-b border-white/10 px-3 py-3 font-medium">注册时间</th>
              <th className="border-b border-white/10 px-3 py-3 font-medium">会员等级</th>
              <th className="border-b border-white/10 px-3 py-3 font-medium">AI调用次数</th>
              <th className="border-b border-white/10 px-3 py-3 font-medium">状态</th>
              <th className="border-b border-white/10 px-3 py-3 font-medium">最近登录时间</th>
              <th className="border-b border-white/10 px-3 py-3 font-medium">操作</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((item) => (
              <tr key={item.user_id} className="border-b border-white/10 bg-[#0d0e10]">
                <td className="px-3 py-3">{item.user_id}</td>
                <td className="px-3 py-3">{item.contact}</td>
                <td className="px-3 py-3">{formatDate(item.registered_at)}</td>
                <td className="px-3 py-3">{item.member_level === "starter" ? "plus" : item.member_level}</td>
                <td className="px-3 py-3">{item.api_call_count}</td>
                <td className="px-3 py-3">{item.status}</td>
                <td className="px-3 py-3">{formatDate(item.last_login_at)}</td>
                <td className="px-3 py-3">
                  <div className="flex flex-wrap gap-2">
                    {item.status === "active" ? (
                      <button
                        onClick={() => runAction(item.user_id, () => banAdminUser(item.user_id, token), "已封号", { status: "banned" })}
                        disabled={busyUserId === item.user_id}
                        className="rounded border border-white/15 px-2 py-1 text-xs text-white/80"
                      >
                        🚫 封号
                      </button>
                    ) : (
                      <button
                        onClick={() => runAction(item.user_id, () => unbanAdminUser(item.user_id, token), "已解封", { status: "active" })}
                        disabled={busyUserId === item.user_id}
                        className="rounded border border-white/15 px-2 py-1 text-xs text-white/80"
                      >
                        ✅ 解封
                      </button>
                    )}
                    <button
                      onClick={() => runAction(item.user_id, () => changeAdminUserMembership(item.user_id, "pro", token), "已升级会员", { member_level: "pro" })}
                      disabled={busyUserId === item.user_id}
                      className="rounded border border-white/15 px-2 py-1 text-xs text-white/80"
                    >
                      ⬆️ 升级会员
                    </button>
                    <button
                      onClick={() => runAction(item.user_id, () => changeAdminUserMembership(item.user_id, "free", token), "已降级会员", { member_level: "free" })}
                      disabled={busyUserId === item.user_id}
                      className="rounded border border-white/15 px-2 py-1 text-xs text-white/80"
                    >
                      ⬇️ 降级会员
                    </button>
                    <button
                      onClick={() => runAction(item.user_id, () => resetAdminUserApiKey(item.user_id, token), "已重置 API Key", {})}
                      disabled={busyUserId === item.user_id}
                      className="rounded border border-white/15 px-2 py-1 text-xs text-white/80"
                    >
                      🔑 重置API Key
                    </button>
                  </div>
                </td>
              </tr>
            ))}
            {!filtered.length ? (
              <tr>
                <td colSpan={8} className="px-3 py-8 text-center text-white/45">
                  没查到匹配用户
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
    </div>
  );
}
