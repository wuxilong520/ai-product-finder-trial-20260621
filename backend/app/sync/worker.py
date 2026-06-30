from __future__ import annotations

import asyncio

from app.sync.retry_queue import retry_queue


class SyncWorker:
    async def drain_retry_queue(self) -> list[dict]:
        processed: list[dict] = []
        while True:
            item = retry_queue.pop()
            if not item:
                break
            processed.append(item)
            await asyncio.sleep(0)
        return processed


sync_worker = SyncWorker()
