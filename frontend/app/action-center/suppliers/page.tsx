import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { TaskDrivenPageShell } from "@/components/action-center/task-driven-page-shell";
import { Card, CardContent, CardHeader, CardTitle, EmptyState } from "@/design-system/components";
import { ROUTES, taskDetailRoute } from "@/config/routes";
import { TOKEN_KEY } from "@/lib/auth";
import { getServerLanguage } from "@/lib/i18n-server";
import { formatPercent, getTaskSnapshots } from "@/lib/task-page-data";

export default async function SupplierPicksPage() {
  const token = (await cookies()).get(TOKEN_KEY)?.value || "";
  if (!token) redirect(ROUTES.login);

  const lang = await getServerLanguage();
  const { tasks, fulls } = await getTaskSnapshots(token, 6);
  const currentTaskId = tasks[0]?.task_id;
  const latestSuccess = fulls.find((item) => item.task.status === "success");
  const supplierSources = latestSuccess?.explain?.supplier_sources || [];
  const providerName = latestSuccess?.explain?.supplier_provider || "—";
  const supplierFit = latestSuccess?.result?.decision_result?.supplier_fit_score;
  const confidence = latestSuccess?.result?.decision_result?.confidence_score;

  const recentCards = fulls
    .filter((item) => item.task.status === "success")
    .slice(0, 3)
    .map((item) => ({
      taskId: item.task.task_id,
      supplierProvider: item.explain?.supplier_provider || "—",
      fitScore: item.result?.decision_result?.supplier_fit_score,
      sourceCount: item.explain?.supplier_sources?.length || 0,
      truthLevel: item.result?.decision_result?.truth_level || item.result?.truth_result?.truth_level || "—",
    }));

  return (
    <TaskDrivenPageShell
      lang={lang}
      activePath="action"
      title="供应商推荐"
      description="这里会直接汇总最近任务里的供应商来源、匹配分和可信度，不再只是告诉你“以后会做”。"
      badge="Supplier Match"
      notice="当前供应商页展示的都是真实任务里已经生成的数据，但它还没有直接连到你的外部平台账号和实时询价，所以这里先做“能看、能跳、能继续判断”。"
      currentTaskId={currentTaskId}
      metrics={[
        { label: "最近任务数", value: `${tasks.length} 个` },
        { label: "最近供应商来源数", value: `${supplierSources.length} 个` },
        { label: "最近供应商匹配分", value: formatPercent(supplierFit) },
        { label: "最近可信度", value: formatPercent(confidence, "0-1") },
      ]}
      highlights={[
        {
          title: "看最新供应商解释",
          description: `当前最新任务使用的供应商来源策略是 ${providerName}。`,
          href: currentTaskId ? taskDetailRoute(currentTaskId) : ROUTES.tasks,
          hrefLabel: "查看任务详情",
          badge: providerName,
        },
        {
          title: "重新发起供应策略任务",
          description: "你可以带新的 supplier strategy 再跑一轮，比较 cheapest / quality / balanced 的差别。",
          href: ROUTES.createTask,
          hrefLabel: "新建任务",
        },
        {
          title: "还没接真实平台账号",
          description: "这一步以后会补成真实店铺和供应链账号接入。现在先去店铺绑定页看准备状态。",
          href: ROUTES.settingsStoreLinks,
          hrefLabel: "查看店铺绑定",
        },
      ]}
    >
      <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
        <CardHeader>
          <CardTitle>最近几次供应商结果</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {recentCards.length ? (
            recentCards.map((item) => (
              <div key={item.taskId} className="rounded-2xl border border-white/8 bg-white/[0.03] p-4">
                <div className="flex items-center justify-between gap-3">
                  <h3 className="text-base font-semibold text-white">任务 #{item.taskId}</h3>
                  <span className="text-xs text-white/40">{item.truthLevel}</span>
                </div>
                <div className="mt-4 space-y-2 text-sm text-white/65">
                  <div>供应商来源：{item.supplierProvider}</div>
                  <div>匹配分：{formatPercent(item.fitScore)}</div>
                  <div>解释里供应源数量：{item.sourceCount} 个</div>
                </div>
              </div>
            ))
          ) : (
            <EmptyState text="当前还没有成功跑完的供应商任务，所以这里还没有可展示的真实来源数据。" />
          )}
        </CardContent>
      </Card>
    </TaskDrivenPageShell>
  );
}
