"use client";

import { useState } from "react";

import { Button, MinimalField, StatusAlert } from "@/design-system/components";
import { ROUTES } from "@/config/routes";
import { login } from "@/lib/api-gateway";
import { getToken, setToken } from "@/lib/auth";
import { Language, t } from "@/lib/i18n";

export function LoginForm({ lang }: { lang: Language }) {
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
      const savedToken = getToken();
      if (!savedToken) {
        throw new Error(text.loginSaveFailed);
      }
      window.location.assign(ROUTES.home);
    } catch (err) {
      setError(err instanceof Error ? err.message : text.loginFailed);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5 px-4 pb-4 pt-2" autoComplete="off">
      <MinimalField
        id="email"
        type="email"
        value={email}
        onChange={setEmail}
        label={text.email}
        placeholder={text.loginEmailPlaceholder}
        autoComplete="off"
      />
      <MinimalField
        id="password"
        type="password"
        value={password}
        onChange={setPassword}
        label={text.password}
        placeholder={text.loginPasswordPlaceholder}
        autoComplete="new-password"
      />

      {error ? <StatusAlert status="error" message={error} /> : null}

      <Button type="submit" className="h-12 w-full" disabled={loading}>
        {loading ? text.loggingIn : text.login}
      </Button>
    </form>
  );
}
