import Link from "next/link";
import type { ReactNode } from "react";

import { ROUTES } from "@/config/routes";

const navItems = [
  { href: ROUTES.systemAdminUsers, label: "👤 用户管理" },
  { href: ROUTES.systemAdminRevenue, label: "💰 收入管理" },
  { href: ROUTES.systemAdmin, label: "⚙️ 系统状态" },
];

export function InternalAdminConsoleLayout({
  currentHref,
  title,
  children,
}: {
  currentHref: string;
  title: string;
  children: ReactNode;
}) {
  return (
    <div className="min-h-screen bg-[#0b0b0c] text-[#f2f2f2]">
      <div className="mx-auto flex min-h-screen max-w-[1600px]">
        <aside className="w-[220px] shrink-0 border-r border-white/10 bg-[#0f1012] px-4 py-6">
          <div className="mb-8">
            <div className="text-sm font-medium text-white/55">商航AI</div>
            <div className="mt-2 text-xl font-semibold text-white">运营管理后台</div>
            <div className="mt-2 text-xs leading-6 text-white/35">仅内部管理员使用</div>
          </div>

          <nav className="space-y-2">
            {navItems.map((item) => {
              const active = item.href === currentHref;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`block rounded-md px-3 py-2 text-sm transition ${
                    active
                      ? "bg-white text-black"
                      : "text-white/70 hover:bg-white/8 hover:text-white"
                  }`}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>

          <div className="mt-8 border-t border-white/10 pt-4">
            <Link href={ROUTES.admin} className="block rounded-md px-3 py-2 text-sm text-white/55 hover:bg-white/8 hover:text-white">
              返回后台入口
            </Link>
          </div>
        </aside>

        <main className="min-w-0 flex-1 px-8 py-6">
          <div className="mb-6 border-b border-white/10 pb-4">
            <h1 className="text-2xl font-semibold text-white">{title}</h1>
          </div>
          {children}
        </main>
      </div>
    </div>
  );
}
