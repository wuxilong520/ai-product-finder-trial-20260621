from __future__ import annotations

from collections import deque


class RetryQueue:
    def __init__(self) -> None:
        self._queue: deque[dict] = deque()

    def push(self, item: dict) -> None:
        self._queue.append(item)

    def pop(self) -> dict | None:
        if not self._queue:
            return None
        return self._queue.popleft()

    def list_items(self) -> list[dict]:
        return list(self._queue)


retry_queue = RetryQueue()
