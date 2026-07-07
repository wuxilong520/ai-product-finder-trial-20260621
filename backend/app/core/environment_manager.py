from __future__ import annotations

from enum import Enum

from app.core.config import settings


class EnvironmentName(str, Enum):
    DEV = "dev"
    STAGING = "staging"
    PRODUCTION = "production"


class EnvironmentManager:
    def current(self) -> str:
        raw = str(settings.app_env or "development").lower()
        if raw in {"prod", "production"}:
            return EnvironmentName.PRODUCTION.value
        if raw in {"stage", "staging"}:
            return EnvironmentName.STAGING.value
        return EnvironmentName.DEV.value

    def is_production(self) -> bool:
        return self.current() == EnvironmentName.PRODUCTION.value


environment_manager = EnvironmentManager()
