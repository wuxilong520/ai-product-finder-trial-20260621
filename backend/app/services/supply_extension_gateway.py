from __future__ import annotations

import re
import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.runtime import AppError
from app.core.security import create_access_token, decrypt_token, encrypt_token, get_password_hash, verify_password
from app.models.data_connection import DataConnection
from app.models.supplier import SupplierExtensionImport
from app.repositories.data_connection import data_connection_repository
from app.schemas.supply_extension import SupplyImportPayload
from app.services.supply_import_service import supply_import_service


SENSITIVE_KEY_PATTERN = re.compile(r"(cookie|session|authorization|password|access[_-]?token|refresh[_-]?token)", re.IGNORECASE)


class SupplyExtensionGateway:
    platform = "1688_extension"
    code_expire_minutes = 10
    token_expire_minutes = 20

    def generate_extension_code(self, db: Session, *, user_id: int, workspace_id: int) -> dict:
        code = self._build_extension_code()
        expires_at = datetime.now(UTC) + timedelta(minutes=self.code_expire_minutes)
        connection_meta = {
            "pending_code_hash": get_password_hash(code),
            "pending_code_expires_at": expires_at.isoformat(),
            "workspace_id": workspace_id,
            "auth_mode": "one_time_code",
            "last_code_issued_at": datetime.now(UTC).isoformat(),
        }
        data_connection_repository.upsert(
            db,
            user_id=user_id,
            workspace_id=workspace_id,
            platform=self.platform,
            status="PENDING",
            encrypted_access_token="",
            encrypted_refresh_token="",
            expires_at=expires_at,
            permission_scope=["supply_extension:import"],
            external_account_id=None,
            connection_meta=connection_meta,
            last_synced_at=None,
            last_sync_error=None,
        )
        return {
            "extension_code": code,
            "expires_in_seconds": self.code_expire_minutes * 60,
            "status": "PENDING",
            "platform": self.platform,
        }

    def exchange_extension_code(self, db: Session, *, extension_code: str) -> dict:
        connection = self._find_connection_by_code(db, extension_code.strip())
        if not connection:
            raise AppError("SUPPLY_EXTENSION_CODE_INVALID", "连接码不对，或者已经失效了。", "supply_extension", 401)

        expires_at = datetime.now(UTC) + timedelta(minutes=self.token_expire_minutes)
        token = create_access_token(
            subject=connection.user_id,
            expires_delta=timedelta(minutes=self.token_expire_minutes),
            extra_payload={
                "workspace_id": (connection.connection_meta or {}).get("workspace_id"),
                "role": "extension",
                "extension_scope": "supply_extension:import",
                "platform": self.platform,
            },
        )
        connection_meta = dict(connection.connection_meta or {})
        connection_meta.pop("pending_code_hash", None)
        connection_meta.pop("pending_code_expires_at", None)
        connection_meta["connected_at"] = datetime.now(UTC).isoformat()
        data_connection_repository.upsert(
            db,
            user_id=connection.user_id,
            workspace_id=(connection.connection_meta or {}).get("workspace_id"),
            platform=self.platform,
            status="CONNECTED",
            encrypted_access_token=encrypt_token(token),
            encrypted_refresh_token="",
            expires_at=expires_at,
            permission_scope=["supply_extension:import"],
            external_account_id=None,
            connection_meta=connection_meta,
            last_synced_at=connection.last_synced_at,
            last_sync_error=None,
        )
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in_seconds": self.token_expire_minutes * 60,
            "platform": self.platform,
            "status": "CONNECTED",
        }

    def import_payload(self, db: Session, *, token_payload: dict, payload: SupplyImportPayload) -> dict:
        self._reject_sensitive_data(payload.model_dump(mode="json"))
        if payload.source != "1688_extension":
            raise AppError("SUPPLY_EXTENSION_SOURCE_INVALID", "插件来源不对，只允许 1688_extension。", "supply_extension", 400)

        user_id = int(token_payload.get("sub") or 0)
        workspace_id = token_payload.get("workspace_id")
        if user_id <= 0:
            raise AppError("SUPPLY_EXTENSION_TOKEN_INVALID", "插件 token 无效，请重新连接。", "supply_extension", 401)

        normalized_record = {
            "keyword": self._guess_keyword(payload),
            "supplier_name": payload.supplier.name.strip(),
            "product_title": payload.title.strip(),
            "product_url": payload.url.strip(),
            "price": self._extract_mid_price(payload.price_range),
            "moq": self._extract_moq(payload.moq),
            "images": payload.images,
            "location": payload.supplier.location,
            "certification": self._string_or_none(payload.metadata.get("certification")),
            "delivery_time": self._extract_delivery_time(payload.metadata),
            "category": self._string_or_none(payload.metadata.get("category")),
        }
        imported = supply_import_service.import_records(db, records=[normalized_record], source_type="browser_extension")
        import_record = SupplierExtensionImport(
            user_id=user_id,
            workspace_id=workspace_id,
            source="1688_extension",
            product_title=payload.title.strip(),
            supplier_name=payload.supplier.name.strip(),
            payload_json=payload.model_dump(mode="json"),
        )
        db.add(import_record)
        db.commit()
        db.refresh(import_record)

        connection = data_connection_repository.get_by_user_platform(db, user_id=user_id, platform=self.platform)
        if connection:
            meta = dict(connection.connection_meta or {})
            meta["last_import_title"] = payload.title.strip()
            meta["last_import_url"] = payload.url.strip()
            if workspace_id is not None:
                meta["workspace_id"] = workspace_id
            data_connection_repository.touch_sync(
                db,
                record=connection,
                status="CONNECTED",
                last_synced_at=datetime.now(UTC),
                last_sync_error=None,
                connection_meta=meta,
            )

        return {
            "imported": bool(imported.get("imported_count")),
            "source_type": "browser_extension",
            "supplier_name": payload.supplier.name.strip(),
            "product_title": payload.title.strip(),
            "keyword": normalized_record["keyword"],
            "import_id": import_record.id,
        }

    def validate_extension_token(self, db: Session, *, raw_token: str) -> dict:
        from app.core.security import decode_access_token

        payload = decode_access_token(raw_token)
        if payload.get("extension_scope") != "supply_extension:import" or payload.get("platform") != self.platform:
            raise AppError("SUPPLY_EXTENSION_TOKEN_FORBIDDEN", "插件 token 权限不对，请重新连接。", "supply_extension", 403)

        user_id = int(payload.get("sub") or 0)
        connection = data_connection_repository.get_by_user_platform(db, user_id=user_id, platform=self.platform)
        if not connection:
            raise AppError("SUPPLY_EXTENSION_CONNECTION_MISSING", "还没有找到插件连接记录。", "supply_extension", 401)
        if connection.status not in {"CONNECTED", "PENDING"}:
            raise AppError("SUPPLY_EXTENSION_CONNECTION_REVOKED", "插件连接已经失效，请重新连接。", "supply_extension", 401)
        if connection.expires_at and self._coerce_utc(connection.expires_at) < datetime.now(UTC):
            raise AppError("SUPPLY_EXTENSION_TOKEN_EXPIRED", "插件 token 已过期，请重新连接。", "supply_extension", 401)
        encrypted = str(connection.encrypted_access_token or "").strip()
        if encrypted:
            try:
                current_token = decrypt_token(encrypted)
                if current_token != raw_token:
                    raise AppError("SUPPLY_EXTENSION_TOKEN_ROTATED", "插件 token 已被刷新，请重新连接。", "supply_extension", 401)
            except AppError:
                raise
        return payload

    def _find_connection_by_code(self, db: Session, code: str) -> DataConnection | None:
        stmt = select(DataConnection).where(DataConnection.platform == self.platform)
        for item in db.scalars(stmt):
            meta = item.connection_meta or {}
            code_hash = str(meta.get("pending_code_hash") or "").strip()
            expires_raw = str(meta.get("pending_code_expires_at") or "").strip()
            if not code_hash or not expires_raw:
                continue
            expires_at = self._coerce_utc(datetime.fromisoformat(expires_raw))
            if expires_at < datetime.now(UTC):
                continue
            if verify_password(code, code_hash):
                return item
        return None

    def _reject_sensitive_data(self, payload: dict) -> None:
        stack: list[tuple[str, object]] = [("root", payload)]
        while stack:
            path, value = stack.pop()
            if isinstance(value, dict):
                for key, nested in value.items():
                    if SENSITIVE_KEY_PATTERN.search(str(key)):
                        raise AppError("SUPPLY_EXTENSION_SENSITIVE_DATA", f"检测到敏感字段 {key}，服务器已拒收。", "supply_extension", 400)
                    stack.append((f"{path}.{key}", nested))
            elif isinstance(value, list):
                for index, nested in enumerate(value):
                    stack.append((f"{path}[{index}]", nested))

    def _build_extension_code(self) -> str:
        return f"SHA-{secrets.token_hex(3).upper()}-{secrets.token_hex(3).upper()}"

    def _guess_keyword(self, payload: SupplyImportPayload) -> str:
        metadata = payload.metadata or {}
        keyword = self._string_or_none(metadata.get("keyword"))
        return keyword or payload.title.strip()

    def _extract_mid_price(self, price_range: str) -> float:
        raw = str(price_range or "")
        numbers = [float(match) for match in re.findall(r"\d+(?:\.\d+)?", raw)]
        if not numbers:
            return 0.0
        if len(numbers) == 1:
            return round(numbers[0], 2)
        return round(sum(numbers[:2]) / 2, 2)

    def _extract_moq(self, moq: str) -> int:
        numbers = re.findall(r"\d+", str(moq or ""))
        return int(numbers[0]) if numbers else 0

    def _extract_delivery_time(self, metadata: dict) -> int | None:
        value = self._string_or_none(metadata.get("delivery_time"))
        if not value:
            return None
        numbers = re.findall(r"\d+", value)
        return int(numbers[0]) if numbers else None

    def _string_or_none(self, value: object) -> str | None:
        text = str(value or "").strip()
        return text or None

    def _coerce_utc(self, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)


supply_extension_gateway = SupplyExtensionGateway()
