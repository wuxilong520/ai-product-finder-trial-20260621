"use client";

import { useEffect, useMemo, useState } from "react";
import { useParams, useRouter } from "next/navigation";

import { ExplainPanel } from "@/components/ExplainPanel";
import { ResultPanel } from "@/components/ResultPanel";
import { TaskStatus } from "@/components/TaskStatus";
import { TracePanel } from "@/components/TracePanel";
import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { Button } from "@/design-system/components";
import { getTaskFull, retryTask } from "@/lib/api/task";
import { getToken } from "@/lib/auth";
import { Language } from "@/lib/i18n";
import { TaskFullResponse } from "@/lib/types";

export default function TaskDetailPage() {
  const params = useParams<{ task_id: string }>();
  const router = useRouter();
  const taskId = Number(params.task_id);
  const token = useMemo(() => getToken(), []);
  const [data, setData] = useState<TaskFullResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [retrying, setRetrying] = useState(false);

  async function loadTask() {
    try {
      const result = await getTaskFull(taskId, token);
      setData(result);
      setError("");
      if (result.task.status === "success" || result.task.status === "failed") {
        return true;
      }
      return false;
    } catch (err) {
      setError(err instanceof Error ? err.message : "读取任务失败");
      return true;
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    let stopped = false;
    let timer: ReturnType<typeof setTimeout> | null = null;

    async function poll() {
      const shouldStop = await loadTask();
      if (!stopped && !shouldStop) {
        timer = setTimeout(poll, 2500);
      }
    }

    poll();
    return () => {
      stopped = true;
      if (timer) clearTimeout(timer);
    };
  }, [taskId]);

  async function handleRetry() {
    try {
      setRetrying(true);
      const token = getToken();
      await retryTask(taskId, token);
      setLoading(true);
      await loadTask();
    } catch (err) {
      setError(err instanceof Error ? err.message : "重试任务失败");
    } finally {
      setRetrying(false);
    }
  }

  return (
    <XBorderLayout lang={"zh" as Language} activePath="action">
      <div className="space-y-6">
        <div className="flex items-center justify-between gap-4">
          <div>
            <div className="text-xs uppercase tracking-[0.24em] text-white/40">Task Detail</div>
            <h1 className="mt-2 text-3xl font-bold text-white">任务详情 #{taskId}</h1>
          </div>
          <div className="flex items-center gap-3">
            {data?.task.status === "failed" ? (
              <Button onClick={handleRetry} disabled={retrying}>
                {retrying ? "重试中..." : "重试任务"}
              </Button>
            ) : null}
            <Button variant="secondary" onClick={() => router.push("/tasks")}>返回任务列表</Button>
          </div>
        </div>

        {loading && !data ? (
          <div className="rounded-3xl border border-white/8 bg-[#111A2E] p-8 text-white/65">
            正在读取任务状态...
          </div>
        ) : null}

        {error ? (
          <div className="rounded-3xl border border-[#FF5C5C]/20 bg-[#FF5C5C]/10 p-6 text-sm text-[#FFD2D2]">
            {error}
          </div>
        ) : null}

        {data ? (
          <>
            <TaskStatus task={data.task} />
            <ResultPanel decision={data.result?.decision_result} truth={data.result?.truth_result} />
            <ExplainPanel explain={data.explain} />
            <TracePanel trace={data.trace} />
          </>
        ) : null}
      </div>
    </XBorderLayout>
  );
}
