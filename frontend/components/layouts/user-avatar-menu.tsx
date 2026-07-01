"use client";

import Link from "next/link";
import { LogOut, Settings, User as UserIcon } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";

import { ROUTES } from "@/config/routes";
import { getCurrentUser } from "@/lib/api";
import { clearToken, getToken } from "@/lib/auth";
import type { User } from "@/lib/types";

function getInitials(user: User | null) {
  const seed = user?.full_name?.trim() || user?.email?.trim() || "U";
  return seed.slice(0, 1).toUpperCase();
}

export function UserAvatarMenu() {
  const [user, setUser] = useState<User | null>(null);
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement | null>(null);

  const displayName = useMemo(() => user?.full_name?.trim() || user?.email || "我的账户", [user]);
  const displayEmail = useMemo(() => user?.email || "未读取到账号信息", [user]);

  useEffect(() => {
    let cancelled = false;

    async function loadUser() {
      const token = getToken();
      if (!token) return;
      try {
        const me = await getCurrentUser(token);
        if (!cancelled) {
          setUser(me);
        }
      } catch {
        if (!cancelled) {
          setUser(null);
        }
      }
    }

    void loadUser();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    function handlePointerDown(event: MouseEvent) {
      if (!rootRef.current) return;
      if (event.target instanceof Node && !rootRef.current.contains(event.target)) {
        setOpen(false);
      }
    }

    function handleEscape(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setOpen(false);
      }
    }

    document.addEventListener("mousedown", handlePointerDown);
    document.addEventListener("keydown", handleEscape);
    return () => {
      document.removeEventListener("mousedown", handlePointerDown);
      document.removeEventListener("keydown", handleEscape);
    };
  }, []);

  function handleLogout() {
    setOpen(false);
    clearToken();
    window.location.assign(ROUTES.login);
  }

  function handleMenuNavigate() {
    setOpen(false);
  }

  return (
    <div ref={rootRef} className="relative hidden md:block">
      <div className="relative">
        <button
          type="button"
          aria-expanded={open}
          aria-haspopup="menu"
          onClick={() => setOpen((current) => !current)}
          className="flex h-11 items-center gap-3 rounded-full border border-white/10 bg-[#111A2E] pl-3 pr-4 text-white/80 transition hover:border-white/20 hover:bg-white/[0.06]"
        >
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[linear-gradient(135deg,#4F7CFF,#6C5CE7)] text-sm font-semibold text-white">
            {getInitials(user)}
          </div>
          <div className="max-w-[120px] truncate text-sm">{displayName}</div>
        </button>

        <div
          className={`absolute right-0 top-[calc(100%+10px)] z-50 w-64 rounded-2xl border border-white/10 bg-[#111A2E] p-3 shadow-[0_18px_40px_rgba(0,0,0,0.28)] transition duration-200 ${
            open ? "pointer-events-auto translate-y-0 opacity-100" : "pointer-events-none translate-y-2 opacity-0"
          }`}
        >
          <div className="rounded-2xl border border-white/8 bg-white/[0.04] p-4">
            <div className="text-sm font-semibold text-white">{displayName}</div>
            <div className="mt-1 truncate text-xs text-white/45">{displayEmail}</div>
          </div>

          <div className="mt-3 space-y-2">
            <Link
              href={ROUTES.settingsProfile}
              onClick={handleMenuNavigate}
              className="flex items-center gap-3 rounded-2xl px-4 py-3 text-sm text-white/80 transition hover:bg-white/[0.06] hover:text-white"
            >
              <UserIcon className="h-4 w-4" />
              <span>个人设置</span>
            </Link>
            <Link
              href={ROUTES.settings}
              onClick={handleMenuNavigate}
              className="flex items-center gap-3 rounded-2xl px-4 py-3 text-sm text-white/80 transition hover:bg-white/[0.06] hover:text-white"
            >
              <Settings className="h-4 w-4" />
              <span>账户中心</span>
            </Link>
            <button
              type="button"
              onClick={handleLogout}
              className="flex w-full items-center gap-3 rounded-2xl px-4 py-3 text-left text-sm text-[#FCA5A5] transition hover:bg-[rgba(239,68,68,0.12)] hover:text-[#FECACA]"
            >
              <LogOut className="h-4 w-4" />
              <span>退出登录</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
