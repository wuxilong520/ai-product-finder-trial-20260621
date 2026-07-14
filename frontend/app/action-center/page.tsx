import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { OperationCenter } from "@/components/operation/operation-center";
import { Card, CardContent, CardHeader, CardTitle } from "@/design-system/components";
import { loadFlowPageData } from "@/lib/flow-page-data";

export default async function ActionCenterPage() {
  const { lang } = await loadFlowPageData();
  const text = lang === "en"
    ? {
        title: "Action Center",
        desc: "Handle AI picks, procurement pool, profit review, supplier suggestions, price comparisons, and execution status in one place.",
        top10: "Top 10 Picks",
        procurement: "Procurement Pool",
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
        title: "商业执行",
        desc: "这里统一处理 AI 推荐商品、采购池、利润分析、供应商推荐、价格对比和执行状态。",
        top10: "推荐商品TOP10",
        procurement: "采购池",
        profit: "利润分析",
        supplier: "供应商推荐",
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
          <CardHeader>
            <CardTitle>{text.title}</CardTitle>
            <p className="text-sm leading-7 text-white/55">{text.desc}</p>
          </CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-6">
            <MetricCard label={text.top10} value={text.single} />
            <MetricCard label={text.procurement} value={text.linked} />
            <MetricCard label={text.profit} value={text.linked} />
            <MetricCard label={text.supplier} value={text.real} />
            <MetricCard label={text.compare} value={text.direct} />
            <MetricCard label={text.queue} value={text.closed} />
          </CardContent>
        </Card>

        <OperationCenter lang={lang} />
      </div>
    </XBorderLayout>
  );
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/8 bg-white/[0.03] px-4 py-4">
      <div className="text-sm text-white/45">{label}</div>
      <div className="mt-2 text-lg font-semibold text-white">{value}</div>
    </div>
  );
}
