import { AuthShell } from "@/components/auth/auth-shell";
import { ForgotPasswordForm } from "@/components/auth/forgot-password-form";
import { getServerLanguage } from "@/lib/i18n-server";

export default async function ForgotPasswordPage() {
  const lang = await getServerLanguage();

  return (
    <AuthShell
      lang={lang}
      title="找回你的登录密码"
      desc="输入邮箱后获取验证码，验证通过后就可以设置新密码。"
      badge="账号安全恢复"
    >
      <ForgotPasswordForm lang={lang} />
    </AuthShell>
  );
}
