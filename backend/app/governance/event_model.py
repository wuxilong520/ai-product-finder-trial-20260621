from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class GovernanceEvent:
    event_id: str
    event_key: str
    task_id: int | None
    workspace_id: int | None
    user_id: int | None
    api_key_id: int | None
    event_type: str
    event_stage: str
    created_at: str


def build_event_key(*, task_id: int | None, event_type: str, pipeline_step: str) -> str:
    return f"{task_id or 'unknown'}:{event_type}:{pipeline_step}"


def build_governance_event(
    *,
    task_id: int | None,
    workspace_id: int | None,
    user_id: int | None,
    api_key_id: int | None,
    event_type: str,
    event_stage: str,
    pipeline_step: str,
) -> GovernanceEvent:
    event_key = build_event_key(task_id=task_id, event_type=event_type, pipeline_step=pipeline_step)
    created_at = datetime.now(timezone.utc).isoformat()
    return GovernanceEvent(
        event_id=event_key,
        event_key=event_key,
        task_id=task_id,
        workspace_id=workspace_id,
        user_id=user_id,
        api_key_id=api_key_id,
        event_type=event_type,
        event_stage=event_stage,
        created_at=created_at,
    )
