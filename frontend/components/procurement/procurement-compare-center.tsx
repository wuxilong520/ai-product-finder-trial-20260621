"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { Button, Card, CardContent, CardHeader, CardTitle, EmptyState, InfoTile } from "@/design-system/components";
import { ROUTES } from "@/config/routes";
import { compareProcurementItems } from "@/lib/api-gateway";
import { getToken } from "@/lib/auth";
import type { ProcurementPoolItem } from "@/lib/types";


export function ProcurementCompareCenter({ ids }: { ids: number[] }) {
  const [items, setItems] = useState<ProcurementPoolItem[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!ids.length) return;
    void (async () => {
      try {
        const result = await compareProcurementItems(ids, getToken());
        setItems(result.items);
      } catch (err) {
        setError(err instanceof Error ? err.message : "读取比较结果失败");
      }
    })();
  }, [ids]);

  return (
    <Card className="border-white/8 bg-[#121c2c] shadow-[0_18px_40px_rgba(0,0,0,0.22)]">
      <CardHeader>
        <CardTitle>智能采购方案对比</CardTitle>
        <p className="text-sm text-white/55">最多同时比较 5 个商品，这里只展示真实采购候选数据。</p>
      </CardHeader>
      <CardContent>
        {error ? <div className="rounded-2xl border border-rose-400/20 bg-rose-400/10 px-4 py-3 text-sm text-rose-200">{error}</div> : null}
        {!ids.length ? (
          <EmptyState
            title="你还没选中要比较的商品"
            text="先去采购方案页勾选 2 到 5 个商品，再回来做采购成本、利润和风险对比。"
            action={<Button asChild><Link href={ROUTES.actionProcurement}>回采购方案选择商品</Link></Button>}
          />
        ) : items.length ? (
          <div className="grid gap-4 xl:grid-cols-3">
            {items.map((item) => (
              <div key={item.id} className="rounded-3xl border border-white/8 bg-white/5 p-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="text-lg font-semibold text-white">{item.title}</div>
                    <div className="mt-1 text-sm text-white/50">商品 #{item.id}</div>
                  </div>
                  {item.image ? <img src={item.image} alt={item.title} className="h-16 w-16 rounded-2xl border border-white/8 object-cover" /> : null}
                </div>
                <div className="mt-4 grid gap-3">
                  <InfoTile label="采购成本" value={`¥${item.min_price.toFixed(2)}`} />
                  <InfoTile label="供应商数量" value={`${item.supplier_count}`} />
                  <InfoTile label="利润空间预测" value={`¥${item.estimated_profit.toFixed(2)}`} />
                  <InfoTile label="市场机会指数" value={item.market_score.toFixed(1)} />
                  <InfoTile label="风险等级" value={item.risk_level} />
                  <InfoTile label="AI进入建议" value={item.analysis?.recommendation || "待分析"} />
                </div>
              </div>
            ))}
          </div>
        ) : (
          <EmptyState title="比较池里还没有可展示的数据" text="可能是商品还没导入成功，或者当前 ID 对应的数据还没有准备好。" />
        )}
      </CardContent>
    </Card>
  );
}
