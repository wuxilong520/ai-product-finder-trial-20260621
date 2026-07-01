import { getTaskFull, getTaskList } from "@/lib/api/task";
import { TaskFullResponse, TaskListItem } from "@/lib/types";

export async function getTaskSnapshots(token: string, limit = 6): Promise<{
  tasks: TaskListItem[];
  fulls: TaskFullResponse[];
}> {
  const tasks = await getTaskList(token);
  const picked = tasks.slice(0, limit);
  const fulls = await Promise.all(
    picked.map(async (task) => {
      try {
        return await getTaskFull(task.task_id, token);
      } catch {
        return null;
      }
    })
  );

  return {
    tasks,
    fulls: fulls.filter((item): item is TaskFullResponse => Boolean(item)),
  };
}

export function formatPercent(value?: number | null, scale: "0-1" | "0-100" = "0-100") {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  if (scale === "0-1") return `${Math.round(value * 100)}%`;
  return `${Math.round(value)}分`;
}

export function formatMoney(value?: number | null, prefix = "¥") {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  return `${prefix}${Number(value).toFixed(2)}`;
}
