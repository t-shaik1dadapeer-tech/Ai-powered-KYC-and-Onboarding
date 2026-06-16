from __future__ import annotations

import uuid

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Customer(Base, TimestampMixin):
    __tablename__ = "customers"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)

    kyc_submissions: Mapped[list[KycSubmission]] = relationship(
        back_populates="customer", cascade="all, delete-orphan"
    )
    risk_assessments: Mapped[list[RiskAssessment]] = relationship(
        back_populates="customer", cascade="all, delete-orphan"
    )


from app.models.kyc import KycSubmission  # noqa: E402
from app.models.risk import RiskAssessment  # noqa: E402
