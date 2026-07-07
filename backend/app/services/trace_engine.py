from __future__ import annotations

from abc import ABC, abstractmethod

from app.core.contracts import TraceNode


class TraceEngineBase(ABC):
    @abstractmethod
    def start(self, *, keyword: str, market: str) -> list[TraceNode]:
        raise NotImplementedError

    @abstractmethod
    def append(self, *, trace: list[TraceNode], step: str, adapter: str | None, message: str, payload: dict | None = None) -> list[TraceNode]:
        raise NotImplementedError


class TraceEngine(TraceEngineBase):
    def start(self, *, keyword: str, market: str) -> list[TraceNode]:
        return [
            TraceNode(
                step="request_received",
                adapter=None,
                status="ok",
                message="已接收分析请求",
                payload={"keyword": keyword, "market": market},
            )
        ]

    def append(self, *, trace: list[TraceNode], step: str, adapter: str | None, message: str, payload: dict | None = None) -> list[TraceNode]:
        trace.append(
            TraceNode(
                step=step,
                adapter=adapter,
                status="ok",
                message=message,
                payload=payload or {},
            )
        )
        return trace


trace_engine: TraceEngineBase = TraceEngine()
