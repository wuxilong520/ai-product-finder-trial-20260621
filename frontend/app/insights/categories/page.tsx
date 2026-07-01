import { HonestStatusPage } from "@/components/shared/honest-status-page";
import { getServerLanguage } from "@/lib/i18n-server";

export default async function InsightsCategoriesPage() {
  const lang = await getServerLanguage();
  return (
    <HonestStatusPage
      lang={lang}
      activePath="insights"
      title="热门类目"
      description="这里先把入口做成真实页面，避免用户点了像没反应。真正的热门类目榜单会在平台数据接入后补上。"
      statusLabel="页面状态"
      statusValue="已独立可访问"
      currentLabel="当前可用"
      currentValue="查看现有任务驱动的类目判断结果"
      nextLabel="后续补齐"
      nextValue="对接真实平台类目热度数据"
    />
  );
}
