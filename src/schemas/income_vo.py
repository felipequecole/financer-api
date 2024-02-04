from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, field_validator

from src.schemas.expense_vo import to_zulu_time


class IncomeVo(BaseModel):
    id: str
    name: str
    month_id: str
    amount: Decimal
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator("id", mode="before")
    @classmethod
    def to_string_uuid(cls, v: UUID) -> str:
        return str(v).upper()

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {
            datetime: to_zulu_time
        }


class IncomeUpdateVo(BaseModel):
    name: Optional[str] = None
    amount: Optional[Decimal] = None

    class Config:
        from_attributes = True
        populate_by_name = True
