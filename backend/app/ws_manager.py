from __future__ import annotations

from collections import defaultdict

from fastapi import WebSocket


class TaskWSManager:
    def __init__(self) -> None:
        self.connections: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(self, task_name: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.connections[task_name].append(websocket)

    def disconnect(self, task_name: str, websocket: WebSocket) -> None:
        sockets = self.connections.get(task_name, [])
        if websocket in sockets:
            sockets.remove(websocket)
        if not sockets and task_name in self.connections:
            del self.connections[task_name]

    async def broadcast(self, task_name: str, payload: dict) -> None:
        sockets = list(self.connections.get(task_name, []))
        dead: list[WebSocket] = []
        for socket in sockets:
            try:
                await socket.send_json(payload)
            except Exception:
                dead.append(socket)
        for socket in dead:
            self.disconnect(task_name, socket)


task_ws_manager = TaskWSManager()
