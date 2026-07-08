import { cookies } from "next/headers";
import Link from "next/link";
import { redirect } from "next/navigation";

import { TaskDrivenPageShell } from "@/components/action-center/task-driven-page-shell";
import { Badge, Card, CardContent, CardHeader, CardTitle, EmptyState, InfoTile, StatusAlert } from "@/design-system/components";
import { StatusBadge } from "@/design-system/components/Badge";
import { ROUTES, taskDetailRoute } from "@/config/routes";
import { TOKEN_KEY } from "@/lib/auth";
import { getExecutionDashboard } from "@/lib/api/task";
import { getServerLanguage } from "@/lib/i18n-server";
import { getTaskSnapshots } from "@/lib/task-page-data";

function mapActionLevelStatus(level?: string) {
  const normalized = String(level || "").toUpperCase();
  if (normalized === "AUTO_LIST") return "success" as const;
  if (normalized === "SCALE") return "running" as const;
  if (normalized === "TEST") return "warning" as const;
  if (normalized === "WATCH") return "blocked" as const;
  return "error" as const;
}

function mapExecutionStatus(status?: string) {
  const normalized = String(status || "").toLowerCase();
  if (normalized.includes("published") || normalized.includes("success") || normalized.includes("ready")) return "success" as const;
  if (normalized.includes("queue") || normalized.includes("queued")) return "running" as const;
  if (normalized.includes("blocked") || normalized.includes("idle")) return "blocked" as const;
  return "warning" as const;
}

function mapActionLevelLabel(level?: string) {
  const normalized = String(level || "").toUpperCase();
  if (!normalized) return "未返回";
  return normalized;
}

export default async function LaunchQueuePage() {
  const token = (await cookies()).get(TOKEN_KEY)?.value || "";
  if (!token) redirect(ROUTES.login);

  const lang = await getServerLanguage();
  const dashboard = await getExecutionDashboard(token);
  const { tasks } = await getTaskSnapshots(token, 8);
  const currentTaskId = tasks[0]?.task_id;

  const records = [...dashboard.records].reverse();
  const latestRecord = records[0];
  const queuedCount = records.filter((item) => String(item.platform_execution_status || "").includes("queue")).length;
  const blockedCount = records.filter((item) => String(item.platform_execution_status || "").includes("blocked")).length;
  const successCount = records.filter((item) => item.success).length;
  const oauthWaitingCount = records.filter((item) => String(item.blocked_reason || "").includes("OAuth")).length;

  return (
    <TaskDrivenPageShell
      lang={lang}
      activePath="action"
      title="Shopify执行页"
      description="这页就是第 8 页：专门看 Shopify 发布执行层。你在这里确认的不是分析结果，而是这条商品到底有没有进入队列、有没有被拦截、有没有拿到执行回执。"
      badge="Execution Page"
      notice="这里不假装说已经真实全自动发货。当前展示的，是系统真实记录到的执行层结果：被拦截、待授权、进入队列、返回回执，都会老老实实展示。"
      currentTaskId={currentTaskId}
      metrics={[
        { label: "执行记录", value: `${records.length} 条` },
        { label: "进入队列", value: `${queuedCount} 条` },
        { label: "被拦截", value: `${blockedCount} 条` },
        { label: "待授权", value: `${oauthWaitingCount} 条` },
      ]}
      highlights={[
        {
          title: "回到利润决策页",
          description: "先做利润判断、上架草稿和发布检查，再来这里看执行结果。",
          href: ROUTES.actionProfit,
          hrefLabel: "进入第 7 页",
        },
        {
          title: "查看店铺绑定",
          description: "如果要继续推进 Shopify 真实授权，先去账户页看店铺配置。",
          href: ROUTES.settingsStoreLinks,
          hrefLabel: "去绑定配置",
        },
        {
          title: "查看完整任务链路",
          description: "如果你想看任务 explain、trace、错误原因，可以回任务中心。",
          href: currentTaskId ? taskDetailRoute(currentTaskId) : ROUTES.tasks,
          hrefLabel: "进入任务中心",
        },
      ]}
    >
      <Card className="border-white/8 bg-[#121c2c] p-6 shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
        <div className="grid gap-4 md:grid-cols-4">
          <StageCard title="先看执行等级" desc="先看是 WATCH、TEST、SCALE 还是 AUTO_LIST。" />
          <StageCard title="再看队列状态" desc="确认这条记录有没有真的进入执行队列。" />
          <StageCard title="再看平台状态" desc="看 Shopify 侧到底返回了什么状态。" />
          <StageCard title="最后看阻塞原因" desc="如果没走通，直接看为什么被卡住。" />
        </div>
      </Card>

      <div className="grid gap-5 xl:grid-cols-[1.05fr_0.95fr]">
        <div className="space-y-5">
          <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <CardTitle>当前最新 Shopify 执行状态</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {latestRecord ? (
                <>
                  <div className="flex flex-wrap gap-3">
                    <StatusBadge status={mapActionLevelStatus(latestRecord.execution_level)} label={`执行等级 ${mapActionLevelLabel(latestRecord.execution_level)}`} />
                    <StatusBadge status={mapExecutionStatus(latestRecord.platform_execution_status)} label={latestRecord.platform_execution_status || "未返回执行状态"} />
                    <Badge variant="neutral">{latestRecord.channel || "shopify"}</Badge>
                  </div>
                  <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                    <InfoTile label="关键词" value={latestRecord.keyword || "—"} />
                    <InfoTile label="市场" value={latestRecord.market || "—"} />
                    <InfoTile label="平台动作" value={latestRecord.platform_action || "—"} />
                    <InfoTile label="执行队列" value={latestRecord.execution_queue_status || "—"} />
                    <InfoTile label="Shopify 商品 ID" value={latestRecord.shopify_product_id || "还没有"} />
                    <InfoTile label="店铺域名" value={latestRecord.shop_domain || "还没有"} />
                  </div>
                  <div className="rounded-2xl border border-white/8 bg-black/10 p-4 text-sm leading-7 text-white/68">
                    {buildExecutionSummary(latestRecord)}
                  </div>
                  <StatusAlert
                    status={mapExecutionStatus(latestRecord.platform_execution_status)}
                    title="执行结论"
                    message={latestRecord.blocked_reason || latestRecord.rollback_reason || "当前这条记录没有额外说明。"}
                  />
                  <div className="rounded-2xl border border-white/8 bg-white/[0.03] p-4 text-sm leading-7 text-white/65">
                    <div>- draft：表示先走草稿或测试动作，不是真实全量发布</div>
                    <div>- queued：表示已经进入执行队列，等待后续步骤</div>
                    <div>- published / ready：表示这条链路已经拿到可继续推进的执行回执</div>
                    <div>- failed / blocked：表示当前被拦截，原因会直接写出来</div>
                  </div>
                </>
              ) : (
                <EmptyState text="当前还没有执行记录。你先去第 7 页跑一次发布前检查或发布动作，这里才会出现真实执行数据。" />
              )}
            </CardContent>
          </Card>

          <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <CardTitle>全部 Shopify 执行记录</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {records.length ? (
                records.slice(0, 12).map((item, index) => (
                  <div key={`${item.keyword}-${item.created_at || index}`} className="rounded-2xl border border-white/8 bg-white/[0.03] p-4">
                    <div className="flex flex-wrap items-center justify-between gap-3">
                      <div>
                        <div className="text-base font-semibold text-white">{item.keyword || "未命名商品"}</div>
                        <div className="mt-1 text-xs text-white/40">{item.created_at || "无时间"}</div>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        <StatusBadge status={mapActionLevelStatus(item.execution_level)} label={mapActionLevelLabel(item.execution_level)} />
                        <StatusBadge status={mapExecutionStatus(item.platform_execution_status)} label={item.platform_execution_status || "未返回"} />
                      </div>
                    </div>
                    <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-4 text-sm text-white/65">
                      <div>平台动作：{item.platform_action || "—"}</div>
                      <div>队列状态：{item.execution_queue_status || "—"}</div>
                      <div>商品 ID：{item.shopify_product_id || "—"}</div>
                      <div>店铺：{item.shop_domain || "—"}</div>
                    </div>
                    <div className="mt-3 rounded-2xl border border-white/8 bg-black/10 px-4 py-3 text-sm leading-7 text-white/68">
                      {buildExecutionSummary(item)}
                    </div>
                    <div className="mt-3 text-sm leading-7 text-white/60">
                      {item.blocked_reason || item.rollback_reason || "当前没有额外错误说明。"}
                    </div>
                  </div>
                ))
              ) : (
                <EmptyState text="还没有执行记录。先去第 7 页跑一次，这里才会出现真实执行日志。" />
              )}
            </CardContent>
          </Card>
        </div>

        <div className="space-y-5">
          <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <CardTitle>执行队列总览</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <InfoTile label="TEST 队列" value={`${dashboard.queue_snapshot.queue_test?.count || 0} 条`} />
                <InfoTile label="SCALE 队列" value={`${dashboard.queue_snapshot.queue_batch?.count || 0} 条`} />
                <InfoTile label="AUTO_LIST 队列" value={`${dashboard.queue_snapshot.queue_auto?.count || 0} 条`} />
                <InfoTile label="成功率" value={`${(dashboard.growth_metrics.execution_success_rate * 100).toFixed(2)}%`} />
              </div>
              <div className="rounded-2xl border border-white/8 bg-white/[0.03] p-4 text-sm leading-7 text-white/65">
                <div>- queue_test：小流量测试</div>
                <div>- queue_batch：批量执行准备</div>
                <div>- queue_auto：自动上架准备</div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <CardTitle>执行结果和收益参考</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <InfoTile label="GMV 估算" value={String(dashboard.growth_metrics.gmv_estimate)} />
                <InfoTile label="转化率" value={`${(dashboard.growth_metrics.conversion_rate * 100).toFixed(2)}%`} />
                <InfoTile label="AI 决策准确率" value={`${(dashboard.growth_metrics.ai_decision_accuracy * 100).toFixed(2)}%`} />
                <InfoTile label="执行成功率" value={`${(dashboard.growth_metrics.execution_success_rate * 100).toFixed(2)}%`} />
              </div>
              <div className="rounded-2xl border border-white/8 bg-white/[0.03] p-4">
                <div className="text-sm font-medium text-white">拦截最多的原因</div>
                <div className="mt-3 space-y-2 text-sm leading-7 text-white/65">
                  {dashboard.insight.most_blocked_decisions.length ? (
                    dashboard.insight.most_blocked_decisions.map((item) => (
                      <div key={`${item.reason}-${item.count}`}>- {item.reason}（{item.count} 次）</div>
                    ))
                  ) : (
                    <div>当前还没有拦截统计</div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
            <CardHeader>
              <CardTitle>如果这里走不通，下一步怎么处理</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm leading-7 text-white/60">
              <div>1. 如果是生产锁拦截，就先去解决生产锁，不要重复点发布。</div>
              <div>2. 如果是 OAuth 没完成，就先去店铺绑定完成授权。</div>
              <div>3. 如果你只是想重新跑一轮任务，直接回任务中心或利润决策页。</div>
              <div className="pt-2">
                <Link href={ROUTES.actionProfit} className="text-cyan-300 hover:text-cyan-200">返回利润决策页 →</Link>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </TaskDrivenPageShell>
  );
}

function StageCard({ title, desc }: { title: string; desc: string }) {
  return (
    <div className="rounded-2xl border border-white/8 bg-white/[0.03] p-4">
      <div className="text-base font-semibold text-white">{title}</div>
      <div className="mt-2 text-sm leading-7 text-white/60">{desc}</div>
    </div>
  );
}

function buildExecutionSummary(item: {
  execution_level?: string;
  platform_execution_status?: string;
  execution_queue_status?: string;
  blocked_reason?: string | null;
  shopify_product_id?: string | null;
}) {
  const level = String(item.execution_level || "").toUpperCase();
  const status = String(item.platform_execution_status || "");
  const queue = String(item.execution_queue_status || "");

  if (item.blocked_reason) {
    return `这条 Shopify 执行记录当前被拦截了，执行等级是 ${level || "未返回"}，主要先看阻塞原因，不要重复推进。`;
  }
  if (/published|success|ready/i.test(status)) {
    return `这条 Shopify 执行记录已经拿到较明确的执行结果了，当前状态是 ${status}，可以继续看商品 ID 和后续动作。`;
  }
  if (/queue/i.test(status) || /queue/i.test(queue)) {
    return `这条 Shopify 执行记录已经进入队列，执行等级是 ${level || "未返回"}，现在更适合继续观察队列变化。`;
  }
  return `这条 Shopify 执行记录还在准备阶段，先看执行等级、平台动作和队列状态，再判断下一步。`;
}
