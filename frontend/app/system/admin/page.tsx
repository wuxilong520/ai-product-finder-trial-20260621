import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { InternalAdminConsoleLayout } from "@/components/admin/internal-admin-console-layout";
import { ROUTES } from "@/config/routes";
import { getAdminSystemStatus } from "@/lib/api/admin";
import { TOKEN_KEY } from "@/lib/auth";

function statusText(value: string) {
  return value;
}

export default async function SystemAdminPage() {
  const token = (await cookies()).get(TOKEN_KEY)?.value || "";
  if (!token) redirect(ROUTES.login);

  const data = await getAdminSystemStatus(token);

  return (
    <InternalAdminConsoleLayout currentHref={ROUTES.systemAdmin} title="系统状态">
      <div className="space-y-6">
        <div className="overflow-x-auto rounded-md border border-white/10">
          <table className="min-w-full border-collapse text-sm">
            <thead className="bg-[#111214] text-left text-white/55">
              <tr>
                <th className="border-b border-white/10 px-3 py-3 font-medium">AI系统</th>
                <th className="border-b border-white/10 px-3 py-3 font-medium">状态</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-white/10 bg-[#0d0e10]"><td className="px-3 py-3">AI Gateway</td><td className="px-3 py-3">{statusText(data.ai_system.gateway)}</td></tr>
              <tr className="border-b border-white/10 bg-[#0d0e10]"><td className="px-3 py-3">DeepSeek</td><td className="px-3 py-3">{statusText(data.ai_system.deepseek)}</td></tr>
              <tr className="border-b border-white/10 bg-[#0d0e10]"><td className="px-3 py-3">OpenAI</td><td className="px-3 py-3">{statusText(data.ai_system.openai)}</td></tr>
              <tr className="border-b border-white/10 bg-[#0d0e10]"><td className="px-3 py-3">Qwen</td><td className="px-3 py-3">{statusText(data.ai_system.qwen)}</td></tr>
            </tbody>
          </table>
        </div>

        <div className="overflow-x-auto rounded-md border border-white/10">
          <table className="min-w-full border-collapse text-sm">
            <thead className="bg-[#111214] text-left text-white/55">
              <tr>
                <th className="border-b border-white/10 px-3 py-3 font-medium">API状态</th>
                <th className="border-b border-white/10 px-3 py-3 font-medium">数值</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-white/10 bg-[#0d0e10]"><td className="px-3 py-3">平均响应时间</td><td className="px-3 py-3">{data.api_status.average_response_ms} ms</td></tr>
              <tr className="border-b border-white/10 bg-[#0d0e10]"><td className="px-3 py-3">错误率</td><td className="px-3 py-3">{data.api_status.error_rate_percent}%</td></tr>
              <tr className="border-b border-white/10 bg-[#0d0e10]"><td className="px-3 py-3">fallback次数</td><td className="px-3 py-3">{data.api_status.fallback_count_24h}</td></tr>
              <tr className="border-b border-white/10 bg-[#0d0e10]"><td className="px-3 py-3">24小时请求数</td><td className="px-3 py-3">{data.api_status.request_count_24h}</td></tr>
            </tbody>
          </table>
        </div>

        <div className="overflow-x-auto rounded-md border border-white/10">
          <table className="min-w-full border-collapse text-sm">
            <thead className="bg-[#111214] text-left text-white/55">
              <tr>
                <th className="border-b border-white/10 px-3 py-3 font-medium">服务器状态</th>
                <th className="border-b border-white/10 px-3 py-3 font-medium">数值</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-white/10 bg-[#0d0e10]"><td className="px-3 py-3">CPU</td><td className="px-3 py-3">{data.server_status.cpu_load_1m}</td></tr>
              <tr className="border-b border-white/10 bg-[#0d0e10]"><td className="px-3 py-3">内存</td><td className="px-3 py-3">{data.server_status.memory_mb} MB</td></tr>
              <tr className="border-b border-white/10 bg-[#0d0e10]"><td className="px-3 py-3">网络状态</td><td className="px-3 py-3">{data.server_status.network_status}</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </InternalAdminConsoleLayout>
  );
}
