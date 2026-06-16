from __future__ import annotations

import uuid
from typing import Dict, Union

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.core.metrics import RISK_ASSESSMENTS_TOTAL, RISK_SCORE_OBSERVATIONS
from app.repositories.customer_repository import CustomerRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.kyc_repository import KycRepository
from app.schemas.risk import RiskScoreResponse

logger = get_logger(__name__)

BASE_SCORE = 50


def score_to_band(score: int) -> str:
    if score <= 33:
        return "low"
    if score <= 66:
        return "medium"
    return "high"


class RiskScoreService:
    def __init__(self, db: Session):
        self._customer_repo = CustomerRepository(db)
        self._kyc_repo = KycRepository(db)
        self._document_repo = DocumentRepository(db)

    def calculate(self, customer_id: uuid.UUID) -> RiskScoreResponse:
        customer = self._customer_repo.get_by_id(customer_id)
        submission = self._kyc_repo.get_latest_by_customer(customer_id)

        factors: Dict[str, Union[str, int, bool]] = {"base_score": BASE_SCORE}
        score = BASE_SCORE

        if customer.status == "kyc_verified":
            score -= 15
            factors["kyc_verified"] = True
        else:
            score += 20
            factors["kyc_verified"] = False

        if submission and submission.status == "verified":
            if submission.pan_record and submission.pan_record.verification_status == "verified":
                score -= 10
                factors["pan_verified"] = True
            if submission.bank_record and submission.bank_record.verification_status == "verified":
                score -= 10
                factors["bank_verified"] = True
        else:
            score += 15
            factors["no_verified_kyc"] = True

        score = max(0, min(100, score))
        band = score_to_band(score)

        assessment = self._document_repo.save_risk_assessment(
            customer_id=customer_id,
            score=score,
            band=band,
            factors=factors,
        )

        RISK_SCORE_OBSERVATIONS.labels(band=band).observe(score)
        RISK_ASSESSMENTS_TOTAL.labels(band=band).inc()
        logger.info("risk_score_calculated", customer_id=str(customer_id), score=score, band=band)

        return RiskScoreResponse(
            customer_id=customer_id,
            score=assessment.score,
            band=assessment.band,
            factors=assessment.factors,
            calculated_at=assessment.calculated_at,
        )
