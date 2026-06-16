from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.risk import RiskScoreRequest, RiskScoreResponse
from app.services.risk_score_service import RiskScoreService

router = APIRouter(tags=["risk"])


@router.post("/risk-score", response_model=RiskScoreResponse)
def calculate_risk_score(
    data: RiskScoreRequest, db: Session = Depends(get_db)
) -> RiskScoreResponse:
    return RiskScoreService(db).calculate(data.customer_id)
