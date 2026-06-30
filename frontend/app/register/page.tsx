import { AuthShell } from "@/components/auth/auth-shell";
import { RegisterForm } from "@/components/auth/register-form";
import { getServerLanguage } from "@/lib/i18n-server";

export default async function RegisterPage() {
  const lang = await getServerLanguage();

  return (
    <AuthShell
      lang={lang}
      title="创建你的工作账号"
      desc="注册后会自动创建你的专属工作区。你可以用密码登录，也可以用邮箱验证码快速登录。"
      badge="SaaS 新用户注册"
    >
      <RegisterForm lang={lang} />
    </AuthShell>
  );
}
