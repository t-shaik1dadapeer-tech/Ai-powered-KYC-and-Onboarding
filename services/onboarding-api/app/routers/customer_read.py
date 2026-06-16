import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.customer import CustomerResponse
from app.services.customer_service import CustomerService

router = APIRouter(tags=["customers"])


@router.get("/customer/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: uuid.UUID, db: Session = Depends(get_db)) -> CustomerResponse:
    return CustomerService(db).get_customer(customer_id)
