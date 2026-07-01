import Link from "next/link";
import { ArrowRight, ShieldCheck, Users } from "lucide-react";

import { Button, Card, CardContent } from "@/design-system/components";
import { ROUTES } from "@/config/routes";

export function AdminEntrancePage({
  isLoggedIn,
  hasAdminAccess,
}: {
  isLoggedIn: boolean;
  hasAdminAccess: boolean;
}) {
  return (
    <div className="relative min-h-screen overflow-hidden bg-app-gradient px-6 py-10 text-app-text-primary">
      <div className="absolute inset-0 bg-app-grid opacity-25" />
      <div className="absolute inset-0 bg-app-radial" />

      <div className="relative mx-auto max-w-5xl space-y-6">
        <Card variant="panel" className="p-8">
          <CardContent className="p-0">
            <div className="inline-flex items-center gap-2 rounded-full border border-app-border bg-white/8 px-4 py-2 text-sm text-app-brand-secondary">
              <ShieldCheck className="h-4 w-4" />
              独立后台入口
            </div>
            <h1 className="mt-5 text-4xl font-semibold tracking-tight text-white">运营后台 / Admin Console</h1>
            <p className="mt-4 max-w-3xl text-sm leading-8 text-app-text-secondary">
              这个网址只给你自己和管理员看，用来查看真实用户、工作区、任务、订单、套餐和额度。普通用户继续走主站，不会进这里。
            </p>

            <div className="mt-8 grid gap-4 md:grid-cols-3">
              {[
                "真实用户与工作区数据",
                "真实任务状态与失败情况",
                "真实订单、套餐和额度使用",
              ].map((item) => (
                <div key={item} className="rounded-2xl border border-app-border bg-white/5 p-4 text-sm text-white/75">
                  <div className="flex items-center gap-3">
                    <Users className="h-4 w-4 text-app-brand-secondary" />
                    <span>{item}</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-8 flex flex-wrap gap-3">
              {isLoggedIn && hasAdminAccess ? (
                <Button asChild size="lg">
                  <Link href={ROUTES.systemAdmin}>
                    进入后台总览
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
              ) : isLoggedIn ? (
                <>
                  <Button asChild size="lg">
                    <Link href={ROUTES.home}>返回主站</Link>
                  </Button>
                  <Button asChild variant="secondary" size="lg">
                    <Link href={ROUTES.settingsProfile}>去个人账户</Link>
                  </Button>
                </>
              ) : (
                <>
                  <Button asChild size="lg">
                    <Link href={ROUTES.login}>
                      管理员登录
                      <ArrowRight className="ml-2 h-4 w-4" />
                    </Link>
                  </Button>
                  <Button asChild variant="secondary" size="lg">
                    <Link href={ROUTES.home}>返回主站首页</Link>
                  </Button>
                </>
              )}
            </div>
          </CardContent>
        </Card>

        <Card className="border-white/8 bg-[#121c2c] p-6">
          <div className="text-sm leading-7 text-white/70">
            {isLoggedIn
              ? hasAdminAccess
                ? "你当前这个账号有后台权限，可以直接进入总览。"
                : "你当前已经登录，但这个账号没有后台权限，所以这里只展示后台入口说明，不会放你进管理页。"
              : "你当前还没登录，所以这里只展示后台入口说明。登录后如果账号有管理员权限，就能进后台总览。"}
          </div>
        </Card>
      </div>
    </div>
  );
}
