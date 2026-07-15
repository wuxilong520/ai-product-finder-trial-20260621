from __future__ import annotations

import unittest
from pathlib import Path
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.database import Base
from app.models.procurement import ProcurementPoolItem, ProcurementSupplierItem
from app.models.supplier import Supplier, SupplierProduct  # noqa: F401
from app.models.user import User  # noqa: F401
from app.services.procurement_pool_service import procurement_pool_service
from app.workspace.model import Workspace  # noqa: F401


class ProcurementWorkspaceIsolationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite:///:memory:", future=True)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine, autoflush=False, autocommit=False, future=True)
        self.db: Session = self.SessionLocal()

        item_a = ProcurementPoolItem(
            user_id=1,
            workspace_id=101,
            product_group_id=None,
            keyword="wireless earbuds",
            category="audio",
            title="Workspace A Earbuds",
            image=None,
            description="A only",
            source_platform="1688",
            source_url="https://example.com/a",
            supplier_count=1,
            min_price=12.0,
            max_price=12.0,
            avg_price=12.0,
            estimated_profit=9.0,
            market_score=76.0,
            status="NEW",
            metadata_json={},
        )
        item_b = ProcurementPoolItem(
            user_id=1,
            workspace_id=202,
            product_group_id=None,
            keyword="wireless earbuds",
            category="audio",
            title="Workspace B Earbuds",
            image=None,
            description="B only",
            source_platform="1688",
            source_url="https://example.com/b",
            supplier_count=1,
            min_price=14.0,
            max_price=14.0,
            avg_price=14.0,
            estimated_profit=10.5,
            market_score=73.0,
            status="NEW",
            metadata_json={},
        )
        self.db.add_all([item_a, item_b])
        self.db.flush()
        self.db.add_all(
            [
                ProcurementSupplierItem(
                    workspace_id=101,
                    pool_item_id=item_a.id,
                    supplier_id=None,
                    supplier_product_id=None,
                    supplier_name="Supplier A",
                    price=12.0,
                    moq=50,
                    delivery_time=7,
                    supplier_score=88.0,
                    risk_score=20.0,
                    supplier_truth_score=90.0,
                    source_type="LOCAL_DATABASE",
                    metadata_json={},
                ),
                ProcurementSupplierItem(
                    workspace_id=202,
                    pool_item_id=item_b.id,
                    supplier_id=None,
                    supplier_product_id=None,
                    supplier_name="Supplier B",
                    price=14.0,
                    moq=60,
                    delivery_time=9,
                    supplier_score=82.0,
                    risk_score=28.0,
                    supplier_truth_score=84.0,
                    source_type="LOCAL_DATABASE",
                    metadata_json={},
                ),
            ]
        )
        self.db.commit()

    def tearDown(self) -> None:
        self.db.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def test_workspace_a_only_sees_workspace_a_pool_items(self) -> None:
        result = procurement_pool_service.list_pool(
            self.db,
            user_id=1,
            workspace_id=101,
            keyword=None,
            category=None,
            price_range=None,
            profit_range=None,
            supplier_score=None,
            risk_level=None,
            sort="latest",
        )
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["items"][0]["title"], "Workspace A Earbuds")

    def test_workspace_b_only_sees_workspace_b_pool_items(self) -> None:
        result = procurement_pool_service.list_pool(
            self.db,
            user_id=1,
            workspace_id=202,
            keyword=None,
            category=None,
            price_range=None,
            profit_range=None,
            supplier_score=None,
            risk_level=None,
            sort="latest",
        )
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["items"][0]["title"], "Workspace B Earbuds")

    def test_compare_respects_workspace(self) -> None:
        all_ids = [row.id for row in self.db.query(ProcurementPoolItem).order_by(ProcurementPoolItem.id.asc()).all()]
        result = procurement_pool_service.compare(
            self.db,
            user_id=1,
            workspace_id=101,
            pool_item_ids=all_ids,
        )
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["items"][0]["title"], "Workspace A Earbuds")


if __name__ == "__main__":
    unittest.main()
