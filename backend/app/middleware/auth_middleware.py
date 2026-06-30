from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RequestAuthContext:
    user_id: int
    workspace_id: int
    role: str
    api_key_id: int | None = None
