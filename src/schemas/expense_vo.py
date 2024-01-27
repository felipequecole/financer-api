from datetime import datetime, timezone
from decimal import Decimal
from typing import Annotated, Optional

from pydantic import BaseModel, Field, field_validator


def to_zulu_time(dt: datetime) -> str:
    return dt.replace(tzinfo=timezone.utc).isoformat()


class ExpenseRequestVo(BaseModel):
    """
    Expense Model: represents a recurrent expense in the database
    """
    name: str
    due_day: int
    amount: Optional[Annotated[Decimal, Field(..., decimal_places=2)]] = Decimal(0.00)
    active: Optional[bool] = True
    active_until: Optional[datetime] = None

    @field_validator("amount", mode="after")
    @classmethod
    def two_decimal_places(cls, v: Decimal) -> Decimal:
        return Decimal(v).quantize(Decimal("0.01"))

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {
            datetime: to_zulu_time
        }


class ExpenseUpdateVo(BaseModel):
    """
    Expense Model: represents a recurrent expense in the database
    """
    name: Optional[str] = None
    due_day: Optional[int] = None
    amount: Optional[Annotated[Decimal, Field(..., decimal_places=2)]] = None
    active: Optional[bool] = None
    active_until: Optional[datetime] = None

    @field_validator("amount", mode="after")
    @classmethod
    def two_decimal_places(cls, v: Decimal) -> Decimal:
        return Decimal(v).quantize(Decimal("0.01"))

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {
            datetime: to_zulu_time
        }


class ExpenseVo(BaseModel):
    """
    Expense Model: represents a recurrent expense in the database
    """
    id: int
    name: str
    due_day: int
    amount: Optional[Decimal] = None
    active: Optional[bool] = True
    active_until: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {
            datetime: to_zulu_time
        }
