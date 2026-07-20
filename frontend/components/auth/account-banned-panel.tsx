import Link from "next/link";

import { AuthShell } from "@/components/auth/auth-shell";
import { ROUTES } from "@/config/routes";
import { Button, StatusAlert } from "@/design-system/components";
import { Language } from "@/lib/i18n";

export function AccountBannedPanel({ lang }: { lang: Language }) {
  return (
    <AuthShell
      lang={lang}
      badge="账户状态异常"
      title="账号已被封号"
      desc="这个账号当前不能继续使用商航AI。请联系团队处理后再重新登录。"
    >
      <div className="space-y-5 px-4 pb-4 pt-2">
        <StatusAlert
          status="blocked"
          title="无法继续访问"
          message="你的账号已被封号，请联系团队处理。处理完成前，这个账号不能继续登录和使用系统。"
        />
        <div className="grid gap-3">
          <Button asChild className="h-12 w-full">
            <Link href={ROUTES.login}>返回登录页</Link>
          </Button>
          <Button asChild variant="secondary" className="h-12 w-full">
            <Link href="mailto:2768624869@qq.com">联系团队</Link>
          </Button>
        </div>
      </div>
    </AuthShell>
  );
}
