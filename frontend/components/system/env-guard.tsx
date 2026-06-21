"use client";

import { AlertTriangle } from "lucide-react";

import { Card } from "@/design-system/components";

export function EnvGuard({
  children,
}: {
  children: React.ReactNode;
}) {
  const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL;

  if (process.env.NODE_ENV === "production" && !apiBase) {
    return (
      <main className="min-h-screen bg-app-gradient px-6 py-10 text-app-text-primary">
        <div className="mx-auto max-w-3xl">
          <Card className="p-8">
            <div className="flex items-center gap-3 text-rose-300">
              <AlertTriangle className="h-6 w-6" />
              <h1 className="text-2xl font-semibold text-white">系统未完成部署配置</h1>
            </div>
            <p className="mt-4 text-base leading-8 text-app-text-secondary">
              现在前端没有拿到公网后端地址，所以页面不能正常工作。请先配置 `NEXT_PUBLIC_API_BASE_URL`，再重新部署。
            </p>
          </Card>
        </div>
      </main>
    );
  }

  return <>{children}</>;
}
