import { HonestStatusPage } from "@/components/shared/honest-status-page";
import { getServerLanguage } from "@/lib/i18n-server";

export default async function InsightsForecastPage() {
  const lang = await getServerLanguage();
  return (
    <HonestStatusPage
      lang={lang}
      activePath="insights"
      title="未来趋势预测"
      description="这个入口现在已经独立出来。当前先用已有任务链路给出趋势说明，真实预测能力要等平台数据接入后再升级。"
      statusLabel="预测状态"
      statusValue="当前为系统内部推演"
      currentLabel="当前可用"
      currentValue="基于任务结果查看趋势解释"
      nextLabel="后续补齐"
      nextValue="接入真实平台长期趋势数据和回测"
    />
  );
}
