import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.kyc import KycStatusResponse, KycSubmitRequest
from app.services.kyc_service import KycService

router = APIRouter(tags=["kyc"])


@router.post("/kyc", response_model=KycStatusResponse, status_code=status.HTTP_201_CREATED)
def submit_kyc(data: KycSubmitRequest, db: Session = Depends(get_db)) -> KycStatusResponse:
    return KycService(db).submit_kyc(data)


@router.get("/kyc-status/{customer_id}", response_model=KycStatusResponse)
def get_kyc_status(customer_id: uuid.UUID, db: Session = Depends(get_db)) -> KycStatusResponse:
    return KycService(db).get_kyc_status(customer_id)
