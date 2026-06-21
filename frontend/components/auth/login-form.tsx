"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { Button, MinimalField, StatusAlert } from "@/design-system/components";
import { login } from "@/lib/api";
import { TOKEN_KEY, setToken } from "@/lib/auth";
import { Language, t } from "@/lib/i18n";

export function LoginForm({ lang }: { lang: Language }) {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const text = t(lang);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const result = await login(email, password);
      setToken(result.access_token);
      document.cookie = `${TOKEN_KEY}=${result.access_token}; path=/; max-age=${60 * 60 * 24 * 7}`;
      router.push("/dashboard");
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : text.loginFailed);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5 px-4 pb-4 pt-2">
      <MinimalField
        id="email"
        type="email"
        value={email}
        onChange={setEmail}
        label={text.email}
        placeholder="admin@example.com"
      />
      <MinimalField
        id="password"
        type="password"
        value={password}
        onChange={setPassword}
        label={text.password}
        placeholder="••••••••"
      />

      {error ? <StatusAlert status="error" message={error} /> : null}

      <Button type="submit" className="h-12 w-full" disabled={loading}>
        {loading ? text.loggingIn : text.login}
      </Button>
    </form>
  );
}
