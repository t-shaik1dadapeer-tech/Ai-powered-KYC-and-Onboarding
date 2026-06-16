from __future__ import annotations

import re
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.validators import IFSC_PATTERN, PAN_PATTERN


class KycSubmitRequest(BaseModel):
    customer_id: uuid.UUID
    pan: str = Field(min_length=10, max_length=10)
    account_number: str = Field(min_length=9, max_length=18)
    ifsc: str = Field(min_length=11, max_length=11)

    @field_validator("pan")
    @classmethod
    def validate_pan(cls, value: str) -> str:
        normalized = value.upper().strip()
        if not PAN_PATTERN.match(normalized):
            raise ValueError("Invalid PAN format. Expected ABCDE1234F")
        return normalized

    @field_validator("ifsc")
    @classmethod
    def validate_ifsc(cls, value: str) -> str:
        normalized = value.upper().strip()
        if not IFSC_PATTERN.match(normalized):
            raise ValueError("Invalid IFSC format")
        return normalized

    @field_validator("account_number")
    @classmethod
    def validate_account(cls, value: str) -> str:
        cleaned = re.sub(r"\s", "", value)
        if not cleaned.isdigit():
            raise ValueError("Account number must be numeric")
        return cleaned


class KycStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    customer_id: uuid.UUID
    kyc_submission_id: uuid.UUID
    status: str
    rejection_reason: Optional[str] = None
    pan_verification_status: Optional[str] = None
    bank_verification_status: Optional[str] = None
    submitted_at: datetime
    verified_at: Optional[datetime] = None
