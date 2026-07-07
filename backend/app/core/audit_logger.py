from __future__ import annotations

import json
from pathlib import Path

from app.core.runtime import LOG_DIR


AUDIT_LOG_FILE = Path(LOG_DIR) / "audit.log"


class AuditLogger:
    def write(self, *, user_id: int | None, action: str, payload: dict) -> None:
        AUDIT_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "user_id": user_id,
            "action": action,
            "payload": payload,
        }
        with AUDIT_LOG_FILE.open("a", encoding="utf-8") as file:
            file.write(json.dumps(entry, ensure_ascii=False) + "\n")


audit_logger = AuditLogger()
