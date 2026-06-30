from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.auth_identity import AuthChallenge, AuthVerificationCode


class AuthIdentityRepository:
    def create_code(self, db: Session, **kwargs) -> AuthVerificationCode:
        record = AuthVerificationCode(**kwargs)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def get_latest_active_code(self, db: Session, email: str, purpose: str) -> AuthVerificationCode | None:
        now = datetime.now(UTC)
        return db.scalar(
            select(AuthVerificationCode)
            .where(
                AuthVerificationCode.email == email,
                AuthVerificationCode.purpose == purpose,
                AuthVerificationCode.used_at.is_(None),
                AuthVerificationCode.expires_at > now,
            )
            .order_by(AuthVerificationCode.id.desc())
        )

    def touch_code_attempt(self, db: Session, record: AuthVerificationCode) -> AuthVerificationCode:
        record.attempt_count += 1
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def mark_code_used(self, db: Session, record: AuthVerificationCode) -> AuthVerificationCode:
        record.used_at = datetime.now(UTC)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def purge_codes(self, db: Session, email: str, purpose: str) -> None:
        db.execute(
            delete(AuthVerificationCode).where(
                AuthVerificationCode.email == email,
                AuthVerificationCode.purpose == purpose,
            )
        )
        db.commit()

    def create_challenge(self, db: Session, **kwargs) -> AuthChallenge:
        record = AuthChallenge(**kwargs)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def get_active_challenge(self, db: Session, challenge_token: str) -> AuthChallenge | None:
        now = datetime.now(UTC)
        return db.scalar(
            select(AuthChallenge).where(
                AuthChallenge.challenge_token == challenge_token,
                AuthChallenge.resolved_at.is_(None),
                AuthChallenge.expires_at > now,
            )
        )

    def touch_challenge_attempt(self, db: Session, record: AuthChallenge) -> AuthChallenge:
        record.attempt_count += 1
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def resolve_challenge(self, db: Session, record: AuthChallenge) -> AuthChallenge:
        record.resolved_at = datetime.now(UTC)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def get_latest_active_challenge_by_email(self, db: Session, email: str, purpose: str) -> AuthChallenge | None:
        now = datetime.now(UTC)
        return db.scalar(
            select(AuthChallenge)
            .where(
                AuthChallenge.email == email,
                AuthChallenge.purpose == purpose,
                AuthChallenge.resolved_at.is_(None),
                AuthChallenge.expires_at > now,
            )
            .order_by(AuthChallenge.id.desc())
        )


auth_identity_repository = AuthIdentityRepository()
