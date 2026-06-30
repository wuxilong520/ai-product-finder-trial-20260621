"use client";

import { Card } from "@/design-system/components";
import { TaskDetailStatusResponse } from "@/lib/types";

export function TaskStatus({ task }: { task: TaskDetailStatusResponse }) {
  const progress = task.progress ?? 0;
  const steps = [
    "Fetching market data...",
    "Matching suppliers...",
    "Calculating cost...",
    "Generating decision...",
  ];
  const currentStep =
    task.current_step ||
    (progress >= 85 ? steps[3] : progress >= 60 ? steps[2] : progress >= 35 ? steps[1] : steps[0]);

  return (
    <Card className="border-white/8 bg-[#111A2E] p-6">
      <div className="space-y-5">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="text-xs uppercase tracking-[0.24em] text-white/40">任务状态</div>
            <h2 className="mt-2 text-2xl font-semibold text-white">任务 #{task.task_id}</h2>
            <p className="mt-2 text-sm text-white/55">系统正在按任务流推进，不需要你手动刷新业务逻辑。</p>
          </div>
          <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-right">
            <div className="text-xs text-white/45">已重试</div>
            <div className="mt-1 text-xl font-semibold text-white">{task.retry_count ?? 0}</div>
          </div>
        </div>

        <div>
          <div className="mb-2 flex items-center justify-between text-sm text-white/55">
            <span>完成进度</span>
            <span>{progress}%</span>
          </div>
          <div className="h-3 overflow-hidden rounded-full bg-white/10">
            <div
              className="h-full rounded-full bg-[linear-gradient(90deg,#4F7CFF,#3DD68C)] transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {task.status === "running" || task.status === "pending" ? (
          <div className="rounded-2xl border border-[#4F7CFF]/20 bg-[#4F7CFF]/10 px-4 py-3 text-sm text-[#CFE0FF]">
            <div>系统正在处理市场、供应、成本和决策步骤。</div>
            <div className="mt-2 text-xs text-[#DCE8FF]">{currentStep}</div>
          </div>
        ) : null}

        {task.status === "failed" && task.last_error ? (
          <div className="rounded-2xl border border-[#FF5C5C]/20 bg-[#FF5C5C]/10 px-4 py-3 text-sm text-[#FFD2D2]">
            失败原因：{task.last_error}
          </div>
        ) : null}
      </div>
    </Card>
  );
}
