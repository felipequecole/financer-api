import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, Column, DECIMAL, DateTime, ForeignKey, Integer, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped
from sqlalchemy.sql import func

from src.database.db import Base


class Expense(Base):
    """
    Expense Model: represents a recurrent expense in the database
    """
    __tablename__ = 'expenses'
    id: Mapped[str] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = Column(String)
    due_day: Mapped[int] = Column(Integer)
    amount: Mapped[Decimal] = Column(DECIMAL)
    active: Mapped[bool] = Column(Boolean, default=True)
    created_at: Mapped[datetime] = Column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = Column(DateTime, onupdate=func.now())
    active_until: Mapped[datetime] = Column(DateTime)


def gen_month_key(year: int, month: int) -> str:
    return f"{year}_{month:02d}"


class Month(Base):
    __tablename__ = 'months'
    db_id: Mapped[str] = Column('id', UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    id: Mapped[str] = Column('slug', String, nullable=True, server_default=text("leavemealone"))
    year: Mapped[int] = Column(Integer)
    month: Mapped[int] = Column(Integer)


class MonthDetails(Base):
    __tablename__ = 'v_month_details'
    db_id: Mapped[str] = Column('id', UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    id: Mapped[str] = Column('slug', String, nullable=True, server_default=text("leavemealone"))
    year: Mapped[int] = Column(Integer)
    month: Mapped[int] = Column(Integer)
    total_income: Mapped[Decimal] = Column(DECIMAL)
    total_expense: Mapped[Decimal] = Column(DECIMAL)
    balance: Mapped[Decimal] = Column(DECIMAL)
    first_date_day: Mapped[int] = Column('first_date', Integer)
    last_date_day: Mapped[int] = Column('last_date', Integer)
    paid: Mapped[bool] = Column(Boolean, default=False)


class Bill(Base):
    """
    Bill Model: Represents one instance (within one month) of an expense
    """
    __tablename__ = 'bills'
    id: Mapped[str] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = Column(String)
    month_id: Mapped[str] = Column(String, ForeignKey(Month.id))
    day: Mapped[int] = Column(Integer)
    amount: Mapped[Decimal] = Column(DECIMAL)
    paid: Mapped[bool] = Column(Boolean, default=False)
    created_at: Mapped[datetime] = Column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = Column(DateTime, onupdate=func.now())
    paid_at: Mapped[datetime] = Column(DateTime)


class Income(Base):
    """
    Income Model: Represents an income value in the database
    """
    __tablename__ = 'income'
    id: Mapped[str] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = Column(String)
    month_id: Mapped[str] = Column(String, ForeignKey(Month.id))
    amount: Mapped[Decimal] = Column(DECIMAL)
    created_at: Mapped[datetime] = Column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = Column(DateTime, onupdate=func.now())
