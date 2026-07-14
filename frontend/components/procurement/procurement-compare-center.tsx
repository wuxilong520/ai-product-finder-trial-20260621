"use client";

import { useEffect, useState } from "react";

import { Card, CardContent, CardHeader, CardTitle, EmptyState, Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/design-system/components";
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
        <CardTitle>采购池商品比较</CardTitle>
        <p className="text-sm text-white/55">最多同时比较 5 个商品，这里只展示真实采购池里已经存在的数据。</p>
      </CardHeader>
      <CardContent>
        {error ? <div className="rounded-2xl border border-rose-400/20 bg-rose-400/10 px-4 py-3 text-sm text-rose-200">{error}</div> : null}
        {!ids.length ? (
          <EmptyState text="你还没选中要比较的商品，先去采购池勾选。" />
        ) : items.length ? (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>商品</TableHead>
                <TableHead>最低价</TableHead>
                <TableHead>供应商</TableHead>
                <TableHead>利润</TableHead>
                <TableHead>市场分</TableHead>
                <TableHead>风险</TableHead>
                <TableHead>建议</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {items.map((item) => (
                <TableRow key={item.id}>
                  <TableCell>{item.title}</TableCell>
                  <TableCell>¥{item.min_price.toFixed(2)}</TableCell>
                  <TableCell>{item.supplier_count}</TableCell>
                  <TableCell>¥{item.estimated_profit.toFixed(2)}</TableCell>
                  <TableCell>{item.market_score.toFixed(1)}</TableCell>
                  <TableCell>{item.risk_level}</TableCell>
                  <TableCell>{item.analysis?.recommendation || "待分析"}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        ) : (
          <EmptyState text="比较池里还没有可展示的数据。" />
        )}
      </CardContent>
    </Card>
  );
}
