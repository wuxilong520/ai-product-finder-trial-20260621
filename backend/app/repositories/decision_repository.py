from __future__ import annotations

from sqlalchemy.orm import Session

from app.governance import lineage_writer
from app.repositories.business_truth_decision import business_truth_decision_repository
from app.repositories.decision_recommendation import decision_recommendation_repository


class DecisionRepository:
    def persist_decision_result(
        self,
        db: Session,
        *,
        task_id: int,
        product_id: int,
        payload: dict,
    ):
        sanitized_payload = {key: value for key, value in payload.items() if key != "task_id"}
        record_payload = {
            **sanitized_payload,
            "result_json": sanitized_payload,
        }
        result = decision_recommendation_repository.upsert(
            db,
            product_id=product_id,
            task_id=task_id,
            **record_payload,
        )
        lineage_writer.write_from_decision(db, sanitized_payload, task_id=task_id)
        return result

    def persist_business_truth_result(
        self,
        db: Session,
        *,
        task_id: int,
        product_id: int,
        payload: dict,
    ):
        sanitized_payload = {key: value for key, value in payload.items() if key != "task_id"}
        record_payload = {
            **sanitized_payload,
            "decision_json": sanitized_payload,
        }
        result = business_truth_decision_repository.upsert(
            db,
            product_id=product_id,
            task_id=task_id,
            **record_payload,
        )
        lineage_writer.write_from_truth(db, sanitized_payload, task_id=task_id)
        return result


decision_repository = DecisionRepository()
