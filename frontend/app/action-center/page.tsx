import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { OperationCenter } from "@/components/operation/operation-center";
import { Card, CardContent, KpiTile, SectionIntro } from "@/design-system/components";
import { loadFlowPageData } from "@/lib/flow-page-data";

export default async function ActionCenterPage() {
  const { lang } = await loadFlowPageData();
  const text = lang === "en"
    ? {
        title: "Action Center",
        desc: "Handle AI picks, procurement pool, profit review, supplier suggestions, price comparisons, and execution status in one place.",
        top10: "Top 10 Picks",
        procurement: "Sourcing Plan",
        profit: "Profit Review",
        supplier: "Supplier Suggestions",
        compare: "Price Compare",
        queue: "Launch Queue",
        single: "One place",
        linked: "Connected view",
        real: "Real link",
        direct: "Direct compare",
        closed: "Closed loop",
      }
    : {
        title: "每日工作台",
        desc: "这里统一处理今日机会、采购方案、利润判断、供应方案和 AI 任务。",
        top10: "推荐商品TOP10",
        procurement: "采购方案",
        profit: "利润判断",
        supplier: "供应方案",
        compare: "价格对比",
        queue: "执行队列",
        single: "统一入口",
        linked: "同页查看",
        real: "真实联动",
        direct: "直接比较",
        closed: "状态闭环",
      };

  return (
    <XBorderLayout lang={lang} activePath="action">
      <div className="space-y-6">
        <Card className="border-white/6 bg-[#111A2E]">
          <CardContent className="p-6">
            <SectionIntro
              eyebrow="商航AI · 每日工作台"
              title="把今天要推进的商品、采购和 AI 任务集中到一个地方"
              description="这里是用户每天进入后最该看的工作首页。你会先看到今日机会、采购建议、风险提醒、AI任务和快捷入口，而不是技术信息。"
            />
            <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-6">
              <KpiTile label={text.top10} value={text.single} hint="今天优先看的机会" />
              <KpiTile label={text.procurement} value={text.linked} hint="候选货源继续筛选" />
              <KpiTile label={text.profit} value={text.linked} hint="继续看利润决策" />
              <KpiTile label={text.supplier} value={text.real} hint="继续比真实供应商" />
              <KpiTile label={text.compare} value={text.direct} hint="直接比较商品差异" />
              <KpiTile label={text.queue} value={text.closed} hint="把动作推进成闭环" />
            </div>
          </CardContent>
        </Card>

        <OperationCenter lang={lang} />
      </div>
    </XBorderLayout>
  );
}
