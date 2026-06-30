import { AuthShell } from "@/components/auth/auth-shell";
import { LoginForm } from "@/components/auth/login-form";
import { t } from "@/lib/i18n";
import { getServerLanguage } from "@/lib/i18n-server";

export default async function LoginPage() {
  const lang = await getServerLanguage();
  const text = t(lang);

  return (
    <AuthShell lang={lang} title={text.loginTitle} desc={text.loginDesc} badge={text.loginBadge}>
      <LoginForm lang={lang} />
    </AuthShell>
  );
}
