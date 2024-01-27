from typing import List

from sqlalchemy.orm import Session
from src.schemas.database import Expense
from src.schemas.expense_vo import ExpenseRequestVo, ExpenseUpdateVo, ExpenseVo


def get_all_expenses(db: Session) -> List[ExpenseVo]:
    db_expenses = db.query(Expense).all()
    return [ExpenseVo.model_validate(expense) for expense in db_expenses]


def get_expense_by_id(db: Session, expense_id: int) -> ExpenseVo | None:
    expense = db.query(ExpenseRequestVo).filter(Expense.id == expense_id).first()
    return ExpenseVo.model_validate(expense)


def create_expense(db: Session, expense: ExpenseRequestVo) -> ExpenseVo:
    db_expense = Expense(**expense.model_dump())
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return ExpenseVo.model_validate(db_expense)


def update_expense(db: Session, expense_id: int, expense: ExpenseUpdateVo):
    current_expense = db.query(Expense).filter(Expense.id == expense_id).first()
    for key, value in expense.model_dump(exclude_unset=True).items():
        setattr(current_expense, key, value)
    db.commit()
    return ExpenseVo.model_validate(current_expense)


def delete_expense(db: Session, expense_id: int):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    db.delete(expense)
    db.commit()
