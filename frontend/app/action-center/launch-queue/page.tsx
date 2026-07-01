import { HonestStatusPage } from "@/components/shared/honest-status-page";
import { getServerLanguage } from "@/lib/i18n-server";

export default async function LaunchQueuePage() {
  const lang = await getServerLanguage();
  return (
    <HonestStatusPage
      lang={lang}
      activePath="action"
      title="上架执行队列"
      description="执行队列已经有真实页面，但还没有接入真实店铺上架动作，所以现在只展示任务流和当前状态。"
      statusLabel="执行状态"
      statusValue="当前为任务驱动状态展示"
      currentLabel="当前可用"
      currentValue="查看任务状态、重试、结果和解释"
      nextLabel="后续补齐"
      nextValue="接入真实店铺后支持一键上架与状态回传"
    />
  );
}
