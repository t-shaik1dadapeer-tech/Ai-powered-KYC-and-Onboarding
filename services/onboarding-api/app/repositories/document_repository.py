import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.risk import RiskAssessment


class DocumentRepository:
    """Persists risk assessments (document verification outcomes aggregated)."""

    def __init__(self, db: Session):
        self._db = db

    def save_risk_assessment(
        self,
        customer_id: uuid.UUID,
        score: int,
        band: str,
        factors: dict,
    ) -> RiskAssessment:
        assessment = RiskAssessment(
            customer_id=customer_id,
            score=score,
            band=band,
            factors=factors,
            calculated_at=datetime.now(timezone.utc),
        )
        self._db.add(assessment)
        self._db.commit()
        self._db.refresh(assessment)
        return assessment
