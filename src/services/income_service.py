from uuid import UUID

from sqlalchemy.orm import Session

from src.schemas.database import Income
from src.schemas.income_vo import IncomeUpdateVo, IncomeVo


class IncomeService:

    #  Todo create vo
    @staticmethod
    def create(db: Session, income: Income) -> IncomeVo:
        db.add(income)
        db.commit()
        db.refresh(income)
        return IncomeVo.model_validate(income)

    @staticmethod
    def get_by_month(db: Session, month_id: int):
        return db.query(Income).filter(Income.month_id == month_id).all()

    @staticmethod
    def get_all_paginated(db: Session, paginate, params):
        return paginate(db.query(Income).order_by(Income.amount),
                        params,
                        transformer=lambda incomes: [IncomeVo.model_validate(income) for income in incomes])

    @staticmethod
    def get_paginated_by_month(db: Session, month_id: str, paginate, params):
        return paginate(db.query(Income).filter(Income.month_id == month_id).order_by(Income.amount),
                        params,
                        transformer=lambda incomes: [IncomeVo.model_validate(income) for income in incomes])

    @staticmethod
    def delete(db: Session, id: str) -> None:
        db_id = UUID(id)
        to_be_deleted = db.query(Income).filter(Income.id == db_id).first()
        db.delete(to_be_deleted)
        db.flush()

    @staticmethod
    def update(db: Session, bill_id: str, updated_income: IncomeUpdateVo) -> IncomeVo:
        db_id = UUID(bill_id)
        current_income = db.query(Income).filter(Income.id == db_id).first()
        for key, value in updated_income.model_dump(exclude_unset=True).items():
            setattr(current_income, key, value)
        db.commit()
        db.refresh(current_income)
        return IncomeVo.model_validate(current_income)
