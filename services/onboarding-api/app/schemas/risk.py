from __future__ import annotations

import uuid
from datetime import datetime
from typing import Dict, Union

from pydantic import BaseModel, Field


class RiskScoreRequest(BaseModel):
    customer_id: uuid.UUID = Field(description="Customer to assess")


class RiskScoreResponse(BaseModel):
    customer_id: uuid.UUID
    score: int = Field(ge=0, le=100)
    band: str
    factors: Dict[str, Union[str, int, bool]]
    calculated_at: datetime
