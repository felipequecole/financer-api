from typing import List
from uuid import UUID

from sqlalchemy.orm import Session

from src.schemas.database import Expense
from src.schemas.expense_vo import ExpenseRequestVo, ExpenseUpdateVo, ExpenseVo


class ExpenseService:

    @staticmethod
    def get_all(db: Session, paginate, params) -> List[ExpenseVo]:
        return paginate(db.query(Expense).order_by(Expense.due_day),
                        params,
                        transformer=lambda expenses: [ExpenseVo.model_validate(expense) for expense in expenses])

    @staticmethod
    def get_all_active(db: Session) -> List[ExpenseVo]:
        db_expenses = db.query(Expense).all()
        return [ExpenseVo.model_validate(expense) for expense in db_expenses]

    @staticmethod
    def get_by_id(db: Session, expense_id: str) -> ExpenseVo | None:
        db_id = UUID(expense_id)
        expense = db.query(Expense).filter(Expense.id == db_id).first()
        return ExpenseVo.model_validate(expense)

    @staticmethod
    def get_list_by_id(db: Session, expense_ids: List[str]) -> List[ExpenseVo] | None:
        db_ids = [UUID(expense_id) for expense_id in expense_ids]
        db_expenses = db.query(Expense).where(Expense.id.in_(db_ids)).all()
        return [ExpenseVo.model_validate(expense) for expense in db_expenses]

    @staticmethod
    def create(db: Session, expense: ExpenseRequestVo) -> ExpenseVo:
        db_expense = Expense(**expense.model_dump())
        db.add(db_expense)
        db.commit()
        db.refresh(db_expense)
        return ExpenseVo.model_validate(db_expense)

    @staticmethod
    def update(db: Session, expense_id: str, expense: ExpenseUpdateVo):
        db_id = UUID(expense_id)
        current_expense = db.query(Expense).filter(Expense.id == db_id).first()
        for key, value in expense.model_dump(exclude_unset=True).items():
            setattr(current_expense, key, value)
        db.commit()
        return ExpenseVo.model_validate(current_expense)

    @staticmethod
    def delete(db: Session, expense_id: str):
        db_id = UUID(expense_id)
        expense = db.query(Expense).filter(Expense.id == db_id).first()
        db.delete(expense)
        db.commit()
        db.flush()
