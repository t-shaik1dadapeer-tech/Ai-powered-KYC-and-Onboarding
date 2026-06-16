from sqlalchemy.orm import Session

from app.core.metrics import BANK_VERIFICATIONS_TOTAL, PAN_VERIFICATIONS_TOTAL
from app.repositories.customer_repository import CustomerRepository
from app.schemas.verification import (
    BankVerifyRequest,
    BankVerifyResponse,
    PanVerifyRequest,
    PanVerifyResponse,
)
from app.services.bank_verification_service import BankVerificationService
from app.services.pan_verification_service import PanVerificationService


class StandaloneVerificationService:
    def __init__(self, db: Session):
        self._customer_repo = CustomerRepository(db)
        self._pan_service = PanVerificationService()
        self._bank_service = BankVerificationService()

    def verify_pan(self, data: PanVerifyRequest) -> PanVerifyResponse:
        self._customer_repo.get_by_id(data.customer_id)
        status, _ = self._pan_service.verify(data.pan)
        PAN_VERIFICATIONS_TOTAL.labels(status=status).inc()
        return PanVerifyResponse(
            customer_id=data.customer_id,
            verification_status=status,
            message="PAN verified successfully",
        )

    def verify_bank(self, data: BankVerifyRequest) -> BankVerifyResponse:
        self._customer_repo.get_by_id(data.customer_id)
        status, _ = self._bank_service.verify(data.account_number, data.ifsc)
        BANK_VERIFICATIONS_TOTAL.labels(status=status).inc()
        return BankVerifyResponse(
            customer_id=data.customer_id,
            verification_status=status,
            message="Bank account verified successfully",
        )
