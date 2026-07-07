from __future__ import annotations

from collections import defaultdict


class ExecutionQueue:
    def __init__(self) -> None:
        self._queues: dict[str, list[dict]] = defaultdict(list)

    def queue_test(self, payload: dict) -> dict:
        item = {"queue": "queue_test", "payload": payload}
        self._queues["queue_test"].append(item)
        return item

    def queue_batch(self, payload: dict) -> dict:
        item = {"queue": "queue_batch", "payload": payload}
        self._queues["queue_batch"].append(item)
        return item

    def queue_auto(self, payload: dict) -> dict:
        item = {"queue": "queue_auto", "payload": payload}
        self._queues["queue_auto"].append(item)
        return item

    def get_queue(self, queue_name: str) -> list[dict]:
        return list(self._queues.get(queue_name, []))

    def snapshot(self) -> dict[str, dict]:
        return {
            queue_name: {
                "count": len(items),
                "latest": items[-1] if items else None,
            }
            for queue_name, items in self._queues.items()
        }


execution_queue = ExecutionQueue()
