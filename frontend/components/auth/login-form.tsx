"use client";

import Link from "next/link";
import { useState } from "react";

import { Button, MinimalField, StatusAlert, Tabs, TabsContent, TabsList, TabsTrigger } from "@/design-system/components";
import { ROUTES } from "@/config/routes";
import { getToken, setToken } from "@/lib/auth";
import { Language, t } from "@/lib/i18n";
import { login, loginWithCode, sendAuthCode } from "@/lib/api";

export function LoginForm({ lang }: { lang: Language }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [code, setCode] = useState("");
  const [challengeToken, setChallengeToken] = useState("");
  const [challengeQuestion, setChallengeQuestion] = useState("");
  const [challengeAnswer, setChallengeAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [sendingCode, setSendingCode] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const text = t(lang);

  async function finishLogin(result: Awaited<ReturnType<typeof login>>) {
    setToken(result.access_token);
    const savedToken = getToken();
    if (!savedToken) {
      throw new Error(text.loginSaveFailed);
    }
    window.location.assign(ROUTES.home);
  }

  async function handlePasswordLogin(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setMessage("");
    try {
      const result = await login(email, password);
      await finishLogin(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : text.loginFailed);
    } finally {
      setLoading(false);
    }
  }

  async function handleCodeLogin(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setMessage("");
    try {
      const result = await loginWithCode(email, code);
      await finishLogin(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "验证码登录失败");
    } finally {
      setLoading(false);
    }
  }

  async function handleSendCode() {
    setSendingCode(true);
    setError("");
    setMessage("");
    try {
      const result = await sendAuthCode(email, "login", challengeToken || undefined, challengeAnswer || undefined);
      if (result.challenge?.required) {
        setChallengeToken(result.challenge.challenge_token);
        setChallengeQuestion(result.challenge.challenge_question);
        setMessage("请先完成安全验证，然后再次点击发送验证码。");
        return;
      }
      setChallengeToken("");
      setChallengeQuestion("");
      setChallengeAnswer("");
      setMessage(result.message || "验证码已发送");
    } catch (err) {
      setError(err instanceof Error ? err.message : "发送验证码失败");
    } finally {
      setSendingCode(false);
    }
  }

  return (
    <Tabs defaultValue="password" className="px-4 pb-4 pt-2">
      <TabsList className="grid w-full grid-cols-2">
        <TabsTrigger value="password">密码登录</TabsTrigger>
        <TabsTrigger value="code">验证码登录</TabsTrigger>
      </TabsList>

      <TabsContent value="password">
        <form onSubmit={handlePasswordLogin} className="space-y-5" autoComplete="off">
          <MinimalField id="email" type="email" value={email} onChange={setEmail} label={text.email} placeholder={text.loginEmailPlaceholder} />
          <MinimalField id="password" type="password" value={password} onChange={setPassword} label={text.password} placeholder={text.loginPasswordPlaceholder} />

          {error ? <StatusAlert status="error" message={error} /> : null}
          {message ? <StatusAlert status="success" message={message} /> : null}

          <Button type="submit" className="h-12 w-full" disabled={loading}>
            {loading ? text.loggingIn : text.login}
          </Button>
        </form>
      </TabsContent>

      <TabsContent value="code">
        <form onSubmit={handleCodeLogin} className="space-y-5" autoComplete="off">
          <MinimalField id="email-code" type="email" value={email} onChange={setEmail} label={text.email} placeholder={text.loginEmailPlaceholder} />
          <div className="grid grid-cols-[1fr_132px] gap-3">
            <MinimalField id="code" type="text" value={code} onChange={setCode} label="邮箱验证码" placeholder="请输入验证码" />
            <div className="pt-8">
              <Button type="button" variant="secondary" className="h-14 w-full" disabled={sendingCode || !email} onClick={handleSendCode}>
                {sendingCode ? "发送中..." : "发送验证码"}
              </Button>
            </div>
          </div>

          {challengeQuestion ? (
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <p className="text-sm text-white/80">{challengeQuestion}</p>
              <div className="mt-3">
                <MinimalField id="challenge-answer" type="text" value={challengeAnswer} onChange={setChallengeAnswer} label="安全验证答案" placeholder="请输入答案后再次发送验证码" />
              </div>
            </div>
          ) : null}

          {error ? <StatusAlert status="error" message={error} /> : null}
          {message ? <StatusAlert status="success" message={message} /> : null}

          <Button type="submit" className="h-12 w-full" disabled={loading}>
            {loading ? "登录中..." : "使用验证码登录"}
          </Button>
        </form>
      </TabsContent>

      <div className="mt-6 text-center text-sm text-white/55">
        还没有账号？{" "}
        <Link href={ROUTES.register} className="text-app-brand-secondary hover:text-white">
          去注册
        </Link>
      </div>
      <div className="mt-2 text-center text-sm text-white/45">
        <Link href={ROUTES.forgotPassword} className="text-app-text-secondary hover:text-white">
          忘记密码
        </Link>
      </div>
    </Tabs>
  );
}
