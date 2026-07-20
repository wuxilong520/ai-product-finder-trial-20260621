"use client";

import Link from "next/link";
import { useState } from "react";

import { Button, MinimalField, Modal, ModalBody, ModalDescription, ModalFooter, ModalHeader, ModalTitle, StatusAlert } from "@/design-system/components";
import { ROUTES } from "@/config/routes";
import { setRefreshToken, setToken } from "@/lib/auth";
import { Language } from "@/lib/i18n";
import { login, registerUser, sendAuthCode } from "@/lib/api";

export function RegisterForm({ lang: _lang }: { lang: Language }) {
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");
  const [code, setCode] = useState("");
  const [challengeToken, setChallengeToken] = useState("");
  const [challengeQuestion, setChallengeQuestion] = useState("");
  const [challengeAnswer, setChallengeAnswer] = useState("");
  const [sendingCode, setSendingCode] = useState(false);
  const [loading, setLoading] = useState(false);
  const [pendingAgreement, setPendingAgreement] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function handleSendCode() {
    setSendingCode(true);
    setError("");
    setMessage("");
    try {
      const result = await sendAuthCode(email, "register", challengeToken || undefined, challengeAnswer || undefined);
      if (result.challenge?.required) {
        setChallengeToken(result.challenge.challenge_token);
        setChallengeQuestion(result.challenge.challenge_question);
        setMessage("请先完成安全验证，然后再次点击发送验证码。");
        return;
      }
      setChallengeToken("");
      setChallengeQuestion("");
      setChallengeAnswer("");
      const devHint = result.dev_code ? ` 当前开发环境验证码：${result.dev_code}` : "";
      setMessage(`${result.message || "验证码已发送"}${devHint}`);
        } catch (err) {
      setError(err instanceof Error ? err.message : "发送验证码失败");
    } finally {
      setSendingCode(false);
    }
  }

  async function doRegister() {
    setLoading(true);
    setError("");
    setMessage("");
    try {
      await registerUser(email, password, code, fullName);
      const loginResult = await login(email, password);
      setToken(loginResult.access_token);
      setRefreshToken(loginResult.refresh_token);
      window.location.assign(ROUTES.home);
    } catch (err) {
      setError(err instanceof Error ? err.message : "注册失败");
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPendingAgreement(true);
  }

  return (
    <>
      <Modal open={pendingAgreement} onClose={() => setPendingAgreement(false)}>
        <ModalHeader>
          <ModalTitle>注册前请先同意相关说明</ModalTitle>
          <ModalDescription>
            继续注册，表示你同意用户协议、隐私政策和服务说明。不同意的话，会返回当前注册页面，不会创建账号。
          </ModalDescription>
        </ModalHeader>
        <ModalBody className="space-y-4">
          <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm leading-7 text-white/75">
            <p>1. 本系统提供商业判断辅助，不直接代替你做最终经营决策。</p>
            <p>2. 你需要保证注册信息真实，并自行保管邮箱、密码、验证码。</p>
            <p>3. 平台会保存必要的任务记录、解释记录、追踪记录，用于功能使用和审计。</p>
            <p>4. 不允许将平台用于违法、侵权、恶意抓取、攻击性测试等行为。</p>
          </div>
          <div className="flex flex-wrap gap-3 text-sm">
            <Link href={ROUTES.terms} className="text-app-brand-secondary hover:text-white" target="_blank">
              查看用户协议
            </Link>
            <Link href={ROUTES.privacy} className="text-app-brand-secondary hover:text-white" target="_blank">
              查看隐私政策
            </Link>
            <Link href={ROUTES.servicePolicy} className="text-app-brand-secondary hover:text-white" target="_blank">
              查看服务说明
            </Link>
          </div>
        </ModalBody>
        <ModalFooter>
          <Button type="button" variant="secondary" onClick={() => setPendingAgreement(false)}>
            不同意，返回当前页
          </Button>
          <Button
            type="button"
            onClick={() => {
              setPendingAgreement(false);
              void doRegister();
            }}
            disabled={loading}
          >
            {loading ? "注册中..." : "我同意，继续注册"}
          </Button>
        </ModalFooter>
      </Modal>

      <form onSubmit={handleSubmit} className="space-y-5" autoComplete="off">
        <MinimalField id="register-email" type="email" value={email} onChange={setEmail} label="邮箱" placeholder="请输入注册邮箱" />
        <MinimalField id="register-name" type="text" value={fullName} onChange={setFullName} label="姓名或团队名称" placeholder="方便你识别当前工作区" />
        <MinimalField id="register-password" type="password" value={password} onChange={setPassword} label="登录密码" placeholder="至少 8 位密码" />
        <div className="grid grid-cols-[1fr_132px] gap-3">
          <MinimalField id="register-code" type="text" value={code} onChange={setCode} label="邮箱验证码" placeholder="请输入验证码" />
          <div className="pt-8">
            <Button type="button" className="h-14 w-full bg-[linear-gradient(135deg,#FB923C,#F97316)] text-white shadow-[0_16px_40px_rgba(249,115,22,0.26)] hover:-translate-y-0.5 hover:shadow-[0_18px_42px_rgba(249,115,22,0.3)]" disabled={sendingCode || !email} onClick={handleSendCode}>
              {sendingCode ? "发送中..." : "发送验证码"}
            </Button>
          </div>
        </div>

        {challengeQuestion ? (
          <div className="rounded-2xl border border-[#FED7AA] bg-[#FFF7ED] p-4">
            <p className="text-sm text-[#9A3412]">{challengeQuestion}</p>
            <div className="mt-3">
              <MinimalField id="register-challenge-answer" type="text" value={challengeAnswer} onChange={setChallengeAnswer} label="安全验证答案" placeholder="请输入答案后再次发送验证码" />
            </div>
          </div>
        ) : null}

        <div className="rounded-2xl border border-[#E7E5E4] bg-[#FAFAF9] px-4 py-3 text-sm leading-7 text-[#475569]">
          点击“创建账号”后，会先让你确认：
          <Link href={ROUTES.terms} className="ml-1 text-app-brand-secondary hover:text-white" target="_blank">用户协议</Link>
          、
          <Link href={ROUTES.privacy} className="text-app-brand-secondary hover:text-white" target="_blank">隐私政策</Link>
          和
          <Link href={ROUTES.servicePolicy} className="ml-1 text-app-brand-secondary hover:text-white" target="_blank">服务说明</Link>
          。
        </div>

        {error ? <StatusAlert status="error" message={error} /> : null}
        {message ? <StatusAlert status="success" message={message} /> : null}

        <Button type="submit" className="h-12 w-full bg-[linear-gradient(135deg,#FB923C,#F97316)] text-white shadow-[0_16px_40px_rgba(249,115,22,0.26)] hover:-translate-y-0.5 hover:shadow-[0_18px_42px_rgba(249,115,22,0.3)]" disabled={loading}>
          {loading ? "准备中..." : "创建账号"}
        </Button>

        <div className="text-center text-sm text-[#64748B]">
          已经有账号了？{" "}
          <Link href={ROUTES.login} className="text-[#F97316] hover:text-[#EA580C]">
            去登录
          </Link>
        </div>
      </form>
    </>
  );
}
