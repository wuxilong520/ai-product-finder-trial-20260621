from __future__ import annotations

import csv
import io
import json
import zipfile
from dataclasses import dataclass
from datetime import UTC, datetime
from xml.etree import ElementTree as ET

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.supplier import Supplier, SupplierPriceHistory, SupplierProduct, SupplySupplierHistory


@dataclass(frozen=True)
class ImportedSupplyRecord:
    keyword: str
    supplier_name: str
    product_title: str
    product_url: str
    price: float
    moq: int
    images: list[str]
    category: str | None
    location: str | None
    certification: str | None
    delivery_time: int | None
    source_type: str


class SupplyImportService:
    def import_records(self, db: Session, *, records: list[dict], source_type: str) -> dict:
        normalized = [self._normalize_record(item, source_type=source_type) for item in records]
        imported = 0
        keywords: list[str] = []
        for record in normalized:
            if not record:
                continue
            imported += 1
            keywords.append(record.keyword)
            self._upsert_record(db, record)
        db.commit()
        return {
            "imported_count": imported,
            "source_type": source_type,
            "keywords": sorted(set(keywords)),
        }

    def parse_upload(self, *, filename: str, content: bytes) -> list[dict]:
        lower_name = filename.lower()
        if lower_name.endswith(".csv"):
            return self._parse_csv(content)
        if lower_name.endswith(".json"):
            return self._parse_json(content)
        if lower_name.endswith(".xlsx"):
            return self._parse_xlsx(content)
        if lower_name.endswith(".xls"):
            raise ValueError("当前只支持 .xlsx，不支持旧版 .xls。")
        raise ValueError("当前只支持 CSV、JSON、XLSX。")

    def _parse_csv(self, content: bytes) -> list[dict]:
        text = content.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))
        return [dict(row) for row in reader]

    def _parse_json(self, content: bytes) -> list[dict]:
        payload = json.loads(content.decode("utf-8"))
        if isinstance(payload, list):
            return [dict(item) for item in payload]
        if isinstance(payload, dict) and isinstance(payload.get("records"), list):
            return [dict(item) for item in payload["records"]]
        raise ValueError("JSON 导入格式不对，必须是数组或 {records:[...]}。")

    def _parse_xlsx(self, content: bytes) -> list[dict]:
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            shared_strings = self._xlsx_shared_strings(archive)
            sheet_names = [name for name in archive.namelist() if name.startswith("xl/worksheets/sheet") and name.endswith(".xml")]
            if not sheet_names:
                return []
            sheet_xml = archive.read(sheet_names[0])
        root = ET.fromstring(sheet_xml)
        namespace = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
        rows: list[list[str]] = []
        for row in root.findall(".//a:sheetData/a:row", namespace):
            values: list[str] = []
            for cell in row.findall("a:c", namespace):
                cell_type = cell.attrib.get("t")
                value_node = cell.find("a:v", namespace)
                raw_value = value_node.text if value_node is not None and value_node.text is not None else ""
                if cell_type == "s" and raw_value.isdigit():
                    idx = int(raw_value)
                    raw_value = shared_strings[idx] if idx < len(shared_strings) else ""
                values.append(raw_value)
            if any(value.strip() for value in values):
                rows.append(values)
        if not rows:
            return []
        headers = [str(item).strip() for item in rows[0]]
        records: list[dict] = []
        for row in rows[1:]:
            item = {}
            for idx, header in enumerate(headers):
                if not header:
                    continue
                item[header] = row[idx] if idx < len(row) else ""
            if any(str(value).strip() for value in item.values()):
                records.append(item)
        return records

    def _xlsx_shared_strings(self, archive: zipfile.ZipFile) -> list[str]:
        if "xl/sharedStrings.xml" not in archive.namelist():
            return []
        root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
        namespace = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
        values: list[str] = []
        for item in root.findall(".//a:si", namespace):
            text_parts = [node.text or "" for node in item.findall(".//a:t", namespace)]
            values.append("".join(text_parts))
        return values

    def _normalize_record(self, item: dict, *, source_type: str) -> ImportedSupplyRecord | None:
        supplier_name = str(item.get("supplier_name") or item.get("supplier") or "").strip()
        product_title = str(item.get("product_title") or item.get("title") or "").strip()
        keyword = str(item.get("keyword") or product_title).strip()
        if not supplier_name or not product_title:
            return None
        return ImportedSupplyRecord(
            keyword=keyword,
            supplier_name=supplier_name,
            product_title=product_title,
            product_url=str(item.get("product_url") or item.get("url") or "").strip(),
            price=self._to_float(item.get("price") or item.get("supplier_price")),
            moq=int(self._to_float(item.get("moq") or item.get("min_order_quantity"))),
            images=self._to_images(item.get("images")),
            category=str(item.get("category") or "").strip() or None,
            location=str(item.get("location") or "").strip() or None,
            certification=str(item.get("certification") or "").strip() or None,
            delivery_time=int(self._to_float(item.get("delivery_time") or 0)) or None,
            source_type=source_type,
        )

    def _upsert_record(self, db: Session, record: ImportedSupplyRecord) -> None:
        supplier = db.scalar(
            select(Supplier)
            .where(Supplier.name == record.supplier_name)
            .where(Supplier.platform == "1688")
        )
        if not supplier:
            supplier = Supplier(
                name=record.supplier_name,
                platform="1688",
                supplier_type="factory",
                location=record.location,
                product_category=record.category,
                min_order_quantity=record.moq,
                price_range={"min": record.price, "max": record.price},
                transaction_score=0.0,
                factory_score=72.0,
                trust_score=76.0,
                certification=record.certification,
                delivery_time_days=record.delivery_time,
                source_type=record.source_type,
                confidence_score=0.82 if record.source_type == "merchant_authorized" else 0.76,
                supplier_verified=record.source_type in {"merchant_authorized", "browser_extension"},
                product_url=record.product_url,
                factory_level="user_import",
                delivery_score=78.0 if record.delivery_time and record.delivery_time <= 7 else 58.0,
                price_history=[{"price": record.price, "source": record.source_type}],
                verification_status="verified" if record.source_type == "merchant_authorized" else "pending",
                is_authorized=record.source_type in {"merchant_authorized", "browser_extension"},
                last_feedback=f"{record.source_type} imported",
                last_verified_time=datetime.now(UTC),
            )
            db.add(supplier)
            db.flush()
        else:
            supplier.location = record.location or supplier.location
            supplier.product_category = record.category or supplier.product_category
            supplier.min_order_quantity = record.moq or supplier.min_order_quantity
            supplier.price_range = {"min": record.price, "max": record.price}
            supplier.certification = record.certification or supplier.certification
            supplier.delivery_time_days = record.delivery_time or supplier.delivery_time_days
            supplier.source_type = record.source_type
            supplier.confidence_score = max(float(supplier.confidence_score or 0), 0.76)
            supplier.supplier_verified = supplier.supplier_verified or record.source_type == "merchant_authorized"
            supplier.product_url = record.product_url or supplier.product_url
            supplier.factory_level = "user_import"
            supplier.delivery_score = 78.0 if record.delivery_time and record.delivery_time <= 7 else 58.0
            supplier.price_history = [*list(supplier.price_history or []), {"price": record.price, "source": record.source_type}][-10:]
            supplier.verification_status = "verified" if record.source_type == "merchant_authorized" else supplier.verification_status
            supplier.last_feedback = f"{record.source_type} imported"
            supplier.last_verified_time = datetime.now(UTC)
            db.add(supplier)
            db.flush()

        product = db.scalar(
            select(SupplierProduct)
            .where(SupplierProduct.supplier_id == supplier.id)
            .where(SupplierProduct.keyword == record.keyword)
            .where(SupplierProduct.product_title == record.product_title)
        )
        if not product:
            product = SupplierProduct(
                supplier_id=supplier.id,
                keyword=record.keyword,
                product_title=record.product_title,
                product_image=record.images[0] if record.images else None,
                product_url=record.product_url,
                price_min=record.price,
                price_max=record.price,
                currency="CNY",
                images=record.images,
                source_type=record.source_type,
                confidence_score=0.82 if record.source_type == "merchant_authorized" else 0.76,
                factory_info="用户导入",
                transaction_info=f"{record.source_type} imported",
                raw_snapshot=record.__dict__,
            )
            db.add(product)
        else:
            product.product_image = record.images[0] if record.images else product.product_image
            product.product_url = record.product_url
            product.price_min = record.price
            product.price_max = record.price
            product.currency = "CNY"
            product.images = record.images
            product.source_type = record.source_type
            product.confidence_score = 0.82 if record.source_type == "merchant_authorized" else 0.76
            product.factory_info = "用户导入"
            product.transaction_info = f"{record.source_type} imported"
            product.raw_snapshot = record.__dict__
            db.add(product)

        db.flush()
        db.add(
            SupplierPriceHistory(
                supplier_id=supplier.id,
                product_id=product.id,
                price=record.price,
                moq=record.moq,
                record_source=record.source_type,
            )
        )

        db.add(
            SupplySupplierHistory(
                supplier_name=record.supplier_name,
                platform="1688",
                keyword=record.keyword,
                product_title=record.product_title,
                product_url=record.product_url,
                source_type=record.source_type,
                price_min=record.price,
                price_max=record.price,
                currency="CNY",
                min_order_quantity=record.moq,
                feedback_status=f"{record.source_type}_imported",
                snapshot=record.__dict__,
            )
        )

    def _to_float(self, value) -> float:
        if value in (None, ""):
            return 0.0
        if isinstance(value, (int, float)):
            return round(float(value), 2)
        cleaned = str(value).strip().replace("¥", "").replace("￥", "").replace(",", "")
        try:
            return round(float(cleaned), 2)
        except ValueError:
            return 0.0

    def _to_images(self, value) -> list[str]:
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str) and value.strip():
            if value.strip().startswith("["):
                try:
                    parsed = json.loads(value)
                    if isinstance(parsed, list):
                        return [str(item).strip() for item in parsed if str(item).strip()]
                except Exception:
                    pass
            return [item.strip() for item in value.split(",") if item.strip()]
        return []


supply_import_service = SupplyImportService()
