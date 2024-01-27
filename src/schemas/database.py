from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, Column, DECIMAL, DateTime, Integer, String
from sqlalchemy.orm import Mapped
from sqlalchemy.sql import func
from src.database.db import Base, engine


class Expense(Base):
    """
    Expense Model: represents a recurrent expense in the database
    """
    __tablename__ = 'expenses'
    id: Mapped[int] = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = Column(String, nullable=False)
    due_day: Mapped[int] = Column(Integer, nullable=False)
    amount: Mapped[Decimal] = Column(DECIMAL)
    active: Mapped[bool] = Column(Boolean, default=True)
    created_at: Mapped[datetime] = Column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = Column(DateTime, onupdate=func.now())
    active_until: Mapped[datetime] = Column(DateTime)


class Bill(Base):
    """
    Bill Model: Represents one instance (within one month) of an expense
    """
    __tablename__ = 'bills'
    id: Mapped[int] = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = Column(String, nullable=False)
    year: Mapped[int] = Column(Integer, index=True)
    month: Mapped[int] = Column(Integer, index=True)
    day: Mapped[int] = Column(Integer, index=True)
    amount: Mapped[Decimal] = Column(DECIMAL, nullable=False)
    paid: Mapped[bool] = Column(Boolean, default=False)
    created_at: Mapped[datetime] = Column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = Column(DateTime, onupdate=func.now())
    paid_at: Mapped[datetime] = Column(DateTime)


class Income(Base):
    """
    Income Model: Represents an income value in the database
    """
    __tablename__ = 'income'
    id: Mapped[int] = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = Column(String, nullable=False)
    year: Mapped[int] = Column(Integer, index=True)
    month: Mapped[int] = Column(Integer, index=True)
    amount: Mapped[Decimal] = Column(DECIMAL, nullable=False)
    created_at: Mapped[datetime] = Column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = Column(DateTime, onupdate=func.now())


# Test only
Base.metadata.create_all(bind=engine)
