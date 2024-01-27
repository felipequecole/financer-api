from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.schemas.expense_vo import ExpenseRequestVo, ExpenseUpdateVo, ExpenseVo
from src.services import expenses as expenses_service

router = APIRouter(prefix="/expenses")


@router.get(path="/", response_model=List[ExpenseVo], response_model_exclude_none=True)
def list_all(db: Session = Depends(get_db)):
    return expenses_service.get_all_expenses(db)


@router.post("/", response_model=ExpenseVo, response_model_exclude_none=True)
def add_expense(expense: ExpenseRequestVo, db: Session = Depends(get_db)):
    return expenses_service.create_expense(db, expense)


@router.patch("/{expense_id}", response_model=ExpenseVo, response_model_exclude_none=True)
def update_expense(expense_id: int, expense: ExpenseUpdateVo, db: Session = Depends(get_db)):
    return expenses_service.update_expense(db, expense_id, expense)


@router.delete("/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    return expenses_service.delete_expense(db, expense_id)
