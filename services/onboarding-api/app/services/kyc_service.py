import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.core.metrics import (
    ACTIVE_KYC_SUBMISSIONS,
    BANK_VERIFICATIONS_TOTAL,
    KYC_SUBMISSIONS_TOTAL,
    PAN_VERIFICATIONS_TOTAL,
)
from app.repositories.customer_repository import CustomerRepository
from app.repositories.kyc_repository import KycRepository
from app.schemas.kyc import KycStatusResponse, KycSubmitRequest
from app.services.bank_verification_service import BankVerificationService
from app.services.pan_verification_service import PanVerificationService, hash_sensitive

logger = get_logger(__name__)


class KycService:
    def __init__(self, db: Session):
        self._customer_repo = CustomerRepository(db)
        self._kyc_repo = KycRepository(db)
        self._pan_service = PanVerificationService()
        self._bank_service = BankVerificationService()

    def submit_kyc(self, data: KycSubmitRequest) -> KycStatusResponse:
        self._customer_repo.get_by_id(data.customer_id)
        submission = self._kyc_repo.create_submission(data.customer_id)

        try:
            pan_status, pan_response = self._pan_service.verify(data.pan)
            PAN_VERIFICATIONS_TOTAL.labels(status=pan_status).inc()
            self._kyc_repo.save_pan_record(
                submission,
                pan_hash=hash_sensitive(data.pan),
                status=pan_status,
                provider_response=pan_response,
            )

            bank_status, bank_response = self._bank_service.verify(data.account_number, data.ifsc)
            BANK_VERIFICATIONS_TOTAL.labels(status=bank_status).inc()
            self._kyc_repo.save_bank_record(
                submission,
                account_hash=hash_sensitive(data.account_number),
                ifsc=data.ifsc,
                status=bank_status,
                provider_response=bank_response,
            )

            submission = self._kyc_repo.update_submission_status(submission, "verified")
            self._customer_repo.update_status(
                self._customer_repo.get_by_id(data.customer_id), "kyc_verified"
            )
            KYC_SUBMISSIONS_TOTAL.labels(status="verified").inc()
            ACTIVE_KYC_SUBMISSIONS.inc()
            logger.info("kyc_submitted", customer_id=str(data.customer_id), status="verified")

        except Exception as exc:
            submission = self._kyc_repo.update_submission_status(
                submission, "rejected", rejection_reason=str(exc)
            )
            KYC_SUBMISSIONS_TOTAL.labels(status="rejected").inc()
            logger.error("kyc_rejected", customer_id=str(data.customer_id), reason=str(exc))
            raise

        return self._build_status_response(submission)

    def get_kyc_status(self, customer_id: uuid.UUID) -> KycStatusResponse:
        self._customer_repo.get_by_id(customer_id)
        submission = self._kyc_repo.get_latest_by_customer(customer_id)
        if submission is None:
            raise NotFoundError(f"No KYC submission for customer {customer_id}")
        return self._build_status_response(submission)

    def _build_status_response(self, submission) -> KycStatusResponse:
        return KycStatusResponse(
            customer_id=submission.customer_id,
            kyc_submission_id=submission.id,
            status=submission.status,
            rejection_reason=submission.rejection_reason,
            pan_verification_status=(
                submission.pan_record.verification_status if submission.pan_record else None
            ),
            bank_verification_status=(
                submission.bank_record.verification_status if submission.bank_record else None
            ),
            submitted_at=submission.submitted_at,
            verified_at=submission.verified_at,
        )
