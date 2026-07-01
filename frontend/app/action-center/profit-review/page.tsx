import { HonestStatusPage } from "@/components/shared/honest-status-page";
import { getServerLanguage } from "@/lib/i18n-server";

export default async function ProfitReviewPage() {
  const lang = await getServerLanguage();
  return (
    <HonestStatusPage
      lang={lang}
      activePath="action"
      title="利润分析"
      description="利润分析已经有真实任务结果支撑，后面会继续拆成更细的利润明细页面。"
      statusLabel="当前来源"
      statusValue="来自任务结果中的 profit_score 和 explain"
      currentLabel="当前可用"
      currentValue="查看任务详情页中的利润估算"
      nextLabel="后续补齐"
      nextValue="拆分成本、运费、平台抽佣等细项图表"
    />
  );
}
