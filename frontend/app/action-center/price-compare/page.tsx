import { HonestStatusPage } from "@/components/shared/honest-status-page";
import { getServerLanguage } from "@/lib/i18n-server";

export default async function PriceComparePage() {
  const lang = await getServerLanguage();
  return (
    <HonestStatusPage
      lang={lang}
      activePath="action"
      title="价格对比"
      description="价格对比页面已经独立出来，避免用户点了还是原地。真正的跨平台价格对比要等真实平台接入。"
      statusLabel="对比状态"
      statusValue="待真实平台价格源接入"
      currentLabel="当前可用"
      currentValue="查看任务结果中的利润和成本估算"
      nextLabel="后续补齐"
      nextValue="做 Amazon / 1688 / Shopify 跨源价格对比"
    />
  );
}
