"use client";

import Link from "next/link";
import { useState } from "react";

import { Button, MinimalField, StatusAlert } from "@/design-system/components";
import { ROUTES } from "@/config/routes";
import { Language } from "@/lib/i18n";
import { resetPassword, sendAuthCode } from "@/lib/api";

export function ForgotPasswordForm({ lang: _lang }: { lang: Language }) {
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [challengeToken, setChallengeToken] = useState("");
  const [challengeQuestion, setChallengeQuestion] = useState("");
  const [challengeAnswer, setChallengeAnswer] = useState("");
  const [sendingCode, setSendingCode] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function handleSendCode() {
    setSendingCode(true);
    setError("");
    setMessage("");
    try {
      const result = await sendAuthCode(email, "reset_password", challengeToken || undefined, challengeAnswer || undefined);
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

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setMessage("");
    try {
      const result = await resetPassword(email, code, newPassword);
      setMessage(result.message || "密码已重置");
    } catch (err) {
      setError(err instanceof Error ? err.message : "重置密码失败");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5 px-4 pb-4 pt-2" autoComplete="off">
      <MinimalField id="forgot-email" type="email" value={email} onChange={setEmail} label="邮箱" placeholder="请输入注册邮箱" />
      <div className="grid grid-cols-[1fr_132px] gap-3">
        <MinimalField id="forgot-code" type="text" value={code} onChange={setCode} label="邮箱验证码" placeholder="请输入验证码" />
        <div className="pt-8">
          <Button type="button" variant="secondary" className="h-14 w-full" disabled={sendingCode || !email} onClick={handleSendCode}>
            {sendingCode ? "发送中..." : "发送验证码"}
          </Button>
        </div>
      </div>
      <MinimalField id="forgot-new-password" type="password" value={newPassword} onChange={setNewPassword} label="新密码" placeholder="请输入新的登录密码" />

      {challengeQuestion ? (
        <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <p className="text-sm text-white/80">{challengeQuestion}</p>
          <div className="mt-3">
            <MinimalField id="forgot-challenge-answer" type="text" value={challengeAnswer} onChange={setChallengeAnswer} label="安全验证答案" placeholder="请输入答案后再次发送验证码" />
          </div>
        </div>
      ) : null}

      {error ? <StatusAlert status="error" message={error} /> : null}
      {message ? <StatusAlert status="success" message={message} /> : null}

      <Button type="submit" className="h-12 w-full" disabled={loading}>
        {loading ? "提交中..." : "重置密码"}
      </Button>

      <div className="text-center text-sm text-white/55">
        想起密码了？{" "}
        <Link href={ROUTES.login} className="text-app-brand-secondary hover:text-white">
          返回登录
        </Link>
      </div>
    </form>
  );
}
