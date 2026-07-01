import { HonestStatusPage } from "@/components/shared/honest-status-page";
import { getServerLanguage } from "@/lib/i18n-server";

export default async function InsightsTrendsPage() {
  const lang = await getServerLanguage();
  return (
    <HonestStatusPage
      lang={lang}
      activePath="insights"
      title="市场趋势"
      description="这里现在是独立可访问的真实页面，不再是点一下又回同一页。趋势能力当前基于现有任务流和演示数据工作。"
      statusLabel="趋势来源"
      statusValue="当前为系统任务结果汇总"
      currentLabel="现在能做什么"
      currentValue="查看现有决策结果里的趋势判断"
      nextLabel="后续补齐"
      nextValue="接入真实平台市场数据后展示实时趋势"
    />
  );
}
