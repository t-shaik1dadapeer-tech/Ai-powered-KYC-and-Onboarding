from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, JsonType


class KycSubmission(Base):
    __tablename__ = "kyc_submissions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    customer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("customers.id"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)
    rejection_reason: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    customer: Mapped["Customer"] = relationship(back_populates="kyc_submissions")
    pan_record: Mapped[Optional["PanRecord"]] = relationship(
        back_populates="kyc_submission", uselist=False, cascade="all, delete-orphan"
    )
    bank_record: Mapped[Optional["BankRecord"]] = relationship(
        back_populates="kyc_submission", uselist=False, cascade="all, delete-orphan"
    )


class PanRecord(Base):
    __tablename__ = "pan_records"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    kyc_submission_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("kyc_submissions.id"), unique=True, nullable=False
    )
    pan_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    verification_status: Mapped[str] = mapped_column(String(32), nullable=False)
    provider_response: Mapped[Optional[dict]] = mapped_column(JsonType, nullable=True)

    kyc_submission: Mapped[KycSubmission] = relationship(back_populates="pan_record")


class BankRecord(Base):
    __tablename__ = "bank_records"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    kyc_submission_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("kyc_submissions.id"), unique=True, nullable=False
    )
    account_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    ifsc: Mapped[str] = mapped_column(String(11), nullable=False)
    verification_status: Mapped[str] = mapped_column(String(32), nullable=False)
    provider_response: Mapped[Optional[dict]] = mapped_column(JsonType, nullable=True)

    kyc_submission: Mapped[KycSubmission] = relationship(back_populates="bank_record")


from app.models.customer import Customer  # noqa: E402
