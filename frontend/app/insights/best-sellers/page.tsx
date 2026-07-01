import { HonestStatusPage } from "@/components/shared/honest-status-page";
import { getServerLanguage } from "@/lib/i18n-server";

export default async function InsightsBestSellersPage() {
  const lang = await getServerLanguage();
  return (
    <HonestStatusPage
      lang={lang}
      activePath="insights"
      title="爆款榜单"
      description="这个页面现在是独立入口，先诚实展示当前能力边界，不再做看起来能点但没内容的情况。"
      statusLabel="榜单状态"
      statusValue="待真实平台榜单接入"
      currentLabel="当前可用"
      currentValue="结合任务结果查看推荐商品优先级"
      nextLabel="后续补齐"
      nextValue="接入真实平台热卖榜与销量数据"
    />
  );
}
