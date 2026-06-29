import { XBorderLayout } from "@/components/layouts/xborder-layout";
import { OperationCenter } from "@/components/operation/operation-center";
import { Card, CardContent, CardHeader, CardTitle } from "@/design-system/components";
import { loadFlowPageData } from "@/lib/flow-page-data";

export default async function ActionCenterPage() {
  const { lang } = await loadFlowPageData();

  return (
    <XBorderLayout lang={lang} activePath="action">
      <div className="space-y-6">
        <Card className="border-white/6 bg-[#111A2E]">
          <CardHeader>
            <CardTitle>商业执行</CardTitle>
            <p className="text-sm leading-7 text-white/55">
              这里统一处理 AI 推荐商品、利润分析、供应商推荐、价格对比和执行状态。
            </p>
          </CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-5">
            <MetricCard label="推荐商品TOP10" value="统一入口" />
            <MetricCard label="利润分析" value="同页查看" />
            <MetricCard label="供应商推荐" value="真实联动" />
            <MetricCard label="价格对比" value="直接比较" />
            <MetricCard label="执行队列" value="状态闭环" />
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
