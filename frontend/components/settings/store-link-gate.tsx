"use client";

import { useState } from "react";

import { FeatureGateModal } from "@/components/billing/feature-gate-modal";
import { Button } from "@/design-system/components";

export function StoreLinkGate() {
  const [open, setOpen] = useState(false);

  return (
    <>
      <FeatureGateModal
        open={open}
        onClose={() => setOpen(false)}
        title="店铺绑定还需要开通后续能力"
        description="当前店铺绑定页面已经独立出来，但还没有接真实店铺平台。你确认后会先跳到套餐页；不确认就留在当前页。"
        requiredPlan="starter / pro / enterprise"
        confirmLabel="确认并去看套餐"
      />
      <Button type="button" onClick={() => setOpen(true)}>
        准备绑定店铺
      </Button>
    </>
  );
}
