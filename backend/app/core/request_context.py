from __future__ import annotations

from contextvars import ContextVar, Token


request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)
user_id_var: ContextVar[int | None] = ContextVar("user_id", default=None)
workspace_id_var: ContextVar[int | None] = ContextVar("workspace_id", default=None)
endpoint_var: ContextVar[str | None] = ContextVar("endpoint", default=None)
method_var: ContextVar[str | None] = ContextVar("method", default=None)


def bind_request_context(*, request_id: str, endpoint: str, method: str) -> dict[str, Token]:
    return {
        "request_id": request_id_var.set(request_id),
        "endpoint": endpoint_var.set(endpoint),
        "method": method_var.set(method),
    }


def bind_user_context(*, user_id: int | None = None, workspace_id: int | None = None) -> dict[str, Token]:
    return {
        "user_id": user_id_var.set(user_id),
        "workspace_id": workspace_id_var.set(workspace_id),
    }


def reset_context(tokens: dict[str, Token]) -> None:
    for variable_name, token in tokens.items():
        if variable_name == "request_id":
            request_id_var.reset(token)
        elif variable_name == "endpoint":
            endpoint_var.reset(token)
        elif variable_name == "method":
            method_var.reset(token)
        elif variable_name == "user_id":
            user_id_var.reset(token)
        elif variable_name == "workspace_id":
            workspace_id_var.reset(token)


def get_request_id() -> str | None:
    return request_id_var.get()


def get_user_id() -> int | None:
    return user_id_var.get()


def get_workspace_id() -> int | None:
    return workspace_id_var.get()


def get_endpoint() -> str | None:
    return endpoint_var.get()


def get_method() -> str | None:
    return method_var.get()
