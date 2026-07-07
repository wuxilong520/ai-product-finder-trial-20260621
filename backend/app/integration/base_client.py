from __future__ import annotations

from collections.abc import Callable


class BaseClient:
    def __init__(self, *, mode: str = "mock"):
        self.mode = (mode or "mock").strip().lower()

    def execute(
        self,
        *,
        mock_handler: Callable[[], dict],
        real_handler: Callable[[], dict] | None = None,
    ) -> dict:
        if self.mode == "real" and real_handler is not None:
            try:
                return real_handler()
            except Exception:
                return mock_handler()
        return mock_handler()
