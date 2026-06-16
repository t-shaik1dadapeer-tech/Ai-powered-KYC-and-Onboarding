from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import NotFoundError
from app.models.kyc import BankRecord, KycSubmission, PanRecord


class KycRepository:
    def __init__(self, db: Session):
        self._db = db

    def create_submission(self, customer_id: uuid.UUID) -> KycSubmission:
        submission = KycSubmission(
            customer_id=customer_id,
            status="pending",
            submitted_at=datetime.now(timezone.utc),
        )
        self._db.add(submission)
        self._db.commit()
        self.db_refresh(submission)
        return submission

    def db_refresh(self, submission: KycSubmission) -> None:
        self._db.refresh(submission)

    def get_latest_by_customer(self, customer_id: uuid.UUID):
        stmt = (
            select(KycSubmission)
            .where(KycSubmission.customer_id == customer_id)
            .options(
                selectinload(KycSubmission.pan_record),
                selectinload(KycSubmission.bank_record),
            )
            .order_by(KycSubmission.submitted_at.desc())
            .limit(1)
        )
        return self._db.scalar(stmt)

    def get_submission_with_details(self, customer_id: uuid.UUID) -> KycSubmission:
        submission = self.get_latest_by_customer(customer_id)
        if submission is None:
            raise NotFoundError(f"No KYC submission for customer {customer_id}")
        return submission

    def save_pan_record(
        self,
        submission: KycSubmission,
        pan_hash: str,
        status: str,
        provider_response: dict,
    ) -> PanRecord:
        record = PanRecord(
            kyc_submission_id=submission.id,
            pan_hash=pan_hash,
            verification_status=status,
            provider_response=provider_response,
        )
        self._db.add(record)
        self._db.commit()
        self._db.refresh(record)
        return record

    def save_bank_record(
        self,
        submission: KycSubmission,
        account_hash: str,
        ifsc: str,
        status: str,
        provider_response: dict,
    ) -> BankRecord:
        record = BankRecord(
            kyc_submission_id=submission.id,
            account_hash=account_hash,
            ifsc=ifsc,
            verification_status=status,
            provider_response=provider_response,
        )
        self._db.add(record)
        self._db.commit()
        self._db.refresh(record)
        return record

    def update_submission_status(
        self,
        submission: KycSubmission,
        status: str,
        rejection_reason: Optional[str] = None,
    ) -> KycSubmission:
        submission.status = status
        submission.rejection_reason = rejection_reason
        if status == "verified":
            submission.verified_at = datetime.now(timezone.utc)
        self._db.add(submission)
        self._db.commit()
        self._db.refresh(submission)
        return submission
