import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate


class CustomerRepository:
    def __init__(self, db: Session):
        self._db = db

    def create(self, data: CustomerCreate) -> Customer:
        customer = Customer(
            full_name=data.full_name,
            email=str(data.email),
            phone=data.phone,
            status="pending",
        )
        self._db.add(customer)
        try:
            self._db.commit()
        except IntegrityError as exc:
            self._db.rollback()
            raise ConflictError(f"Customer with email {data.email} already exists") from exc
        self._db.refresh(customer)
        return customer

    def get_by_id(self, customer_id: uuid.UUID) -> Customer:
        customer = self._db.get(Customer, customer_id)
        if customer is None:
            raise NotFoundError(f"Customer {customer_id} not found")
        return customer

    def get_by_email(self, email: str):
        stmt = select(Customer).where(Customer.email == email)
        return self._db.scalar(stmt)

    def update_status(self, customer: Customer, status: str) -> Customer:
        customer.status = status
        self._db.add(customer)
        self._db.commit()
        self._db.refresh(customer)
        return customer
