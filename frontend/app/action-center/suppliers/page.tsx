import { HonestStatusPage } from "@/components/shared/honest-status-page";
import { getServerLanguage } from "@/lib/i18n-server";

export default async function SupplierPicksPage() {
  const lang = await getServerLanguage();
  return (
    <HonestStatusPage
      lang={lang}
      activePath="action"
      title="供应商推荐"
      description="供应商推荐现在已经有任务链路，但还没接到你的真实外部平台账号，所以先把入口做真，把边界说清楚。"
      statusLabel="当前来源"
      statusValue="来自现有供应链决策结果"
      currentLabel="当前可用"
      currentValue="查看供应商推荐结果和解释信息"
      nextLabel="后续补齐"
      nextValue="接入真实平台供应商账号与实时报价"
    />
  );
}
