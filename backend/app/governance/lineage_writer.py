from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.governance.event_model import build_governance_event
from app.repositories.data_governance import data_lineage_repository


class LineageWriter:
    def write_event_if_not_exists(
        self,
        db: Session,
        *,
        event_type: str,
        event_stage: str,
        pipeline_step: str,
        task_id: int | None,
        workspace_id: int | None,
        user_id: int | None,
        api_key_id: int | None,
        source_id: str,
        node_type: str,
        payload_json: dict,
        lineage_chain: list[str] | None = None,
        transform_steps: list[str] | None = None,
    ) -> bool:
        event = build_governance_event(
            task_id=task_id,
            workspace_id=workspace_id,
            user_id=user_id,
            api_key_id=api_key_id,
            event_type=event_type,
            event_stage=event_stage,
            pipeline_step=pipeline_step,
        )
        existing = data_lineage_repository.get_by_event_key(db, event.event_key)
        if existing:
            data_lineage_repository.update_existing(
                db,
                existing,
                workspace_id=workspace_id,
                task_id=task_id,
                user_id=user_id,
                api_key_id=api_key_id,
                source_id=source_id,
                provider_name=node_type,
                node_type=node_type,
                lineage_chain=list(lineage_chain or []),
                transform_steps=list(transform_steps or []),
                payload_json=payload_json,
            )
            return False
        data_lineage_repository.create(
            db,
            event_id=event.event_id,
            event_key=event.event_key,
            event_stage=event.event_stage,
            workspace_id=workspace_id,
            task_id=task_id,
            user_id=user_id,
            api_key_id=api_key_id,
            source_id=source_id,
            provider_name=node_type,
            node_type=node_type,
            lineage_chain=list(lineage_chain or []),
            transform_steps=list(transform_steps or []),
            payload_json=payload_json,
            created_at=event.created_at or datetime.now(timezone.utc).isoformat(),
        )
        return True

    def write_from_decision(self, db: Session, payload: dict, *, task_id: int | None = None) -> None:
        self.write_event_if_not_exists(
            db,
            event_type="decision",
            event_stage="decision_result_persist",
            pipeline_step="decision_result_persist",
            task_id=task_id,
            workspace_id=payload.get("workspace_id"),
            user_id=payload.get("user_id"),
            api_key_id=payload.get("api_key_id"),
            source_id=payload.get("source_id") or f"decision:{task_id or 'unknown'}",
            node_type="decision",
            payload_json=payload,
            lineage_chain=payload.get("lineage_chain", []),
            transform_steps=["decision_result_persist"],
        )

    def write_from_truth(self, db: Session, payload: dict, *, task_id: int | None = None) -> None:
        self.write_event_if_not_exists(
            db,
            event_type="truth",
            event_stage="truth_result_persist",
            pipeline_step="truth_result_persist",
            task_id=task_id,
            workspace_id=payload.get("workspace_id"),
            user_id=payload.get("user_id"),
            api_key_id=payload.get("api_key_id"),
            source_id=payload.get("source_id") or f"truth:{task_id or 'unknown'}",
            node_type="truth",
            payload_json=payload,
            lineage_chain=payload.get("lineage_chain", []),
            transform_steps=["truth_result_persist"],
        )

    def write_from_explain(
        self,
        db: Session,
        payload: dict,
        *,
        task_id: int | None = None,
        workspace_id: int | None = None,
        user_id: int | None = None,
        source_id: str | None = None,
    ) -> None:
        self.write_event_if_not_exists(
            db,
            event_type="explain",
            event_stage="explain_result_persist",
            pipeline_step="explain_result_persist",
            task_id=task_id,
            workspace_id=workspace_id,
            user_id=user_id,
            api_key_id=payload.get("api_key_id"),
            source_id=source_id or f"explain:{task_id or 'unknown'}",
            node_type="explain",
            payload_json=payload,
            lineage_chain=payload.get("data_lineage", []),
            transform_steps=["explain_result_persist"],
        )

    def write_from_trace(
        self,
        db: Session,
        payload: dict,
        *,
        task_id: int | None = None,
        workspace_id: int | None = None,
        user_id: int | None = None,
        source_id: str | None = None,
    ) -> None:
        self.write_event_if_not_exists(
            db,
            event_type="trace",
            event_stage="trace_result_persist",
            pipeline_step="trace_result_persist",
            task_id=task_id,
            workspace_id=workspace_id,
            user_id=user_id,
            api_key_id=payload.get("api_key_id"),
            source_id=source_id or payload.get("source_id") or f"trace:{task_id or 'unknown'}",
            node_type="trace",
            payload_json=payload,
            lineage_chain=payload.get("lineage_chain", []),
            transform_steps=["trace_result_persist"],
        )


lineage_writer = LineageWriter()
