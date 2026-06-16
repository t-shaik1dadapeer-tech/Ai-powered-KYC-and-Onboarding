import uuid

from pydantic import BaseModel, Field, field_validator

from app.schemas.validators import IFSC_PATTERN, PAN_PATTERN


class PanVerifyRequest(BaseModel):
    customer_id: uuid.UUID
    pan: str = Field(min_length=10, max_length=10)

    @field_validator("pan")
    @classmethod
    def validate_pan(cls, value: str) -> str:
        normalized = value.upper().strip()
        if not PAN_PATTERN.match(normalized):
            raise ValueError("Invalid PAN format. Expected ABCDE1234F")
        return normalized


class PanVerifyResponse(BaseModel):
    customer_id: uuid.UUID
    verification_status: str
    message: str


class BankVerifyRequest(BaseModel):
    customer_id: uuid.UUID
    account_number: str = Field(min_length=9, max_length=18)
    ifsc: str = Field(min_length=11, max_length=11)

    @field_validator("ifsc")
    @classmethod
    def validate_ifsc(cls, value: str) -> str:
        normalized = value.upper().strip()
        if not IFSC_PATTERN.match(normalized):
            raise ValueError("Invalid IFSC format")
        return normalized


class BankVerifyResponse(BaseModel):
    customer_id: uuid.UUID
    verification_status: str
    message: str
