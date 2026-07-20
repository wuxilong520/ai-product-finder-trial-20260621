"use client";

import Link from "next/link";

import { Card, Button } from "@/design-system/components";
import { taskDetailRoute } from "@/config/routes";
import { TaskDetailStatusResponse } from "@/lib/types";

export function TaskCard({ task }: { task: TaskDetailStatusResponse }) {
  const statusClass =
    task.status === "success"
      ? "border-[#3DD68C]/20 bg-[#3DD68C]/10 text-[#B7FFD8]"
      : task.status === "failed"
        ? "border-[#FF5C5C]/20 bg-[#FF5C5C]/10 text-[#FFD2D2]"
        : task.status === "running"
          ? "border-[#4F7CFF]/20 bg-[#4F7CFF]/10 text-[#CFE0FF]"
          : "border-white/10 bg-white/5 text-white/70";

  return (
    <Card className="border-white/8 bg-[#111A2E] p-5">
      <div className="space-y-4">
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="text-xs uppercase tracking-[0.22em] text-white/40">商航AI分析</div>
            <div className="mt-2 text-lg font-semibold text-white">分析任务 #{task.task_id}</div>
          </div>
          <div className={`rounded-full border px-3 py-1 text-xs ${statusClass}`}>
            {String(task.status)}
          </div>
        </div>
        <div className="space-y-2 text-sm text-white/55">
          <div>当前进度 {task.progress ?? 0}% · 重试 {task.retry_count ?? 0} 次</div>
          <div className="text-white/40">这条任务会沉淀分析结论、原因说明和下一步建议。</div>
        </div>
        <Button asChild size="sm" className="w-full">
          <Link href={taskDetailRoute(task.task_id)}>查看完整分析报告</Link>
        </Button>
      </div>
    </Card>
  );
}
