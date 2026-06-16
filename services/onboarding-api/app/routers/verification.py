from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.verification import (
    BankVerifyRequest,
    BankVerifyResponse,
    PanVerifyRequest,
    PanVerifyResponse,
)
from app.services.standalone_verification_service import StandaloneVerificationService

router = APIRouter(tags=["verification"])


@router.post("/pan-verify", response_model=PanVerifyResponse)
def verify_pan(data: PanVerifyRequest, db: Session = Depends(get_db)) -> PanVerifyResponse:
    return StandaloneVerificationService(db).verify_pan(data)


@router.post("/bank-verify", response_model=BankVerifyResponse)
def verify_bank(data: BankVerifyRequest, db: Session = Depends(get_db)) -> BankVerifyResponse:
    return StandaloneVerificationService(db).verify_bank(data)
