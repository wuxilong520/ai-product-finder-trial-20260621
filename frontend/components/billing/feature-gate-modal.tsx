"use client";

import { useRouter } from "next/navigation";

import { ROUTES } from "@/config/routes";
import { Button, Modal, ModalBody, ModalDescription, ModalFooter, ModalHeader, ModalTitle } from "@/design-system/components";

type FeatureGateModalProps = {
  open: boolean;
  onClose: () => void;
  title?: string;
  description?: string;
  requiredPlan?: string;
  confirmLabel?: string;
  targetHref?: string;
};

export function FeatureGateModal({
  open,
  onClose,
  title = "当前功能需要升级套餐",
  description = "开通后才能继续使用这个功能。你确认后会跳到套餐与充值页面，不确认就留在当前页面。",
  requiredPlan = "starter / pro / enterprise",
  confirmLabel = "去开通",
  targetHref = ROUTES.pricing,
}: FeatureGateModalProps) {
  const router = useRouter();

  function handleUpgrade() {
    onClose();
    router.push(targetHref);
  }

  return (
    <Modal open={open} onClose={onClose}>
      <ModalHeader>
        <ModalTitle>{title}</ModalTitle>
        <ModalDescription>{description}</ModalDescription>
      </ModalHeader>
      <ModalBody>
        <div className="rounded-2xl border border-white/8 bg-white/5 p-4 text-sm text-white/75">
          建议套餐：<span className="font-semibold text-white">{requiredPlan}</span>
        </div>
      </ModalBody>
      <ModalFooter>
        <Button variant="secondary" onClick={onClose}>
          暂不升级
        </Button>
        <Button onClick={handleUpgrade}>
          {confirmLabel}
        </Button>
      </ModalFooter>
    </Modal>
  );
}
