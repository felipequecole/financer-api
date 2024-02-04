from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class MonthCreateRequest(BaseModel):
    """
    Month Model: represents a month in the database
    """
    year: int = Field(..., gte=2023)
    month: int = Field(..., gt=0, lte=12)
    expenses: list[str] = Field(..., min_items=1)
    income_value: Optional[Decimal] = None

    class Config:
        from_attributes = True
        populate_by_name = True


class MonthDetailsVo(BaseModel):
    id: str
    year: int
    month: int
    total_expense: Optional[Decimal] = None
    total_income: Optional[Decimal] = None
    balance: Optional[Decimal] = None
    first_date_day: Optional[int] = None
    last_date_day: Optional[int] = None
    paid: Optional[bool] = False

    class Config:
        from_attributes = True
        populate_by_name = True
