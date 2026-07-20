import { HonestStatusPage } from "@/components/shared/honest-status-page";
import { getServerLanguage } from "@/lib/i18n-server";

export default async function InsightsRisksPage() {
  const lang = await getServerLanguage();
  return (
    <HonestStatusPage
      lang={lang}
      activePath="insights"
      title="风险提示"
      description="这里后面会承接真正的风险规则和平台异常监控。当前先给用户一个真实、能访问、能理解的页面。"
      statusLabel="风险能力"
      statusValue="当前来自任务结果中的风险指数"
      currentLabel="当前可用"
      currentValue="查看任务详情里的风险评分和解释"
      nextLabel="后续补齐"
      nextValue="接入真实平台风控、侵权、价格波动告警"
    />
  );
}
