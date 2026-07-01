import { HonestStatusPage } from "@/components/shared/honest-status-page";
import { getServerLanguage } from "@/lib/i18n-server";

export default async function ProductComparePage() {
  const lang = await getServerLanguage();
  return (
    <HonestStatusPage
      lang={lang}
      activePath="products"
      title="商品对比"
      description="这个页面现在已经是独立入口，不再是假跳转。当前先提供真实状态说明，等你后面补商品平台接入后，这里会接真实对比能力。"
      statusLabel="页面状态"
      statusValue="已独立可访问"
      currentLabel="当前可用"
      currentValue="从任务结果和商品详情进入商品判断流程"
      nextLabel="后续补齐"
      nextValue="接入真实平台商品后做多商品横向对比"
    />
  );
}
