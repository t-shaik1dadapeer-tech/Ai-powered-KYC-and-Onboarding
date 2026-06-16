import uuid

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.core.metrics import CUSTOMERS_CREATED_TOTAL
from app.repositories.customer_repository import CustomerRepository
from app.schemas.customer import CustomerCreate, CustomerResponse

logger = get_logger(__name__)


class CustomerService:
    def __init__(self, db: Session):
        self._repo = CustomerRepository(db)

    def create_customer(self, data: CustomerCreate) -> CustomerResponse:
        existing = self._repo.get_by_email(str(data.email))
        if existing:
            from app.core.exceptions import ConflictError

            raise ConflictError(f"Customer with email {data.email} already exists")

        customer = self._repo.create(data)
        CUSTOMERS_CREATED_TOTAL.labels(status=customer.status).inc()
        logger.info("customer_created", customer_id=str(customer.id), email=customer.email)
        return CustomerResponse.model_validate(customer)

    def get_customer(self, customer_id: uuid.UUID) -> CustomerResponse:
        customer = self._repo.get_by_id(customer_id)
        return CustomerResponse.model_validate(customer)
