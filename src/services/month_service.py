import sqlalchemy
from sqlalchemy.orm import Session

from src.errors.UserError import UserError
from src.schemas.database import Bill, Income, Month, MonthDetails
from src.schemas.month_vo import MonthCreateRequest, MonthDetailsVo
from src.services.bill_service import BillService
from src.services.expenses_service import ExpenseService
from src.services.income_service import IncomeService


class MonthService:
    @staticmethod
    def create(month_spec: MonthCreateRequest, db: Session):
        try:
            month = Month(year=month_spec.year, month=month_spec.month)
            month = MonthService.save(month, db)
        except sqlalchemy.exc.IntegrityError as e:
            raise UserError("Month already exists", e)

        expenses = ExpenseService.get_list_by_id(db, month_spec.expenses)

        bills = [Bill(
            name=expense.name,
            month_id=month.id,
            day=expense.due_day,
            amount=expense.amount,
            paid=False
        ) for expense in expenses]
        BillService.save_all(db, bills)

        if (month_spec.income_value):
            income = Income(name='Salary', month_id=month.id, amount=month_spec.income_value)
            IncomeService.create(db, income)

        return MonthService.get_details(month.id, db)

    @staticmethod
    def delete(month_id: str, db: Session):
        month = db.query(Month).filter(Month.id == month_id).first()
        if not month:
            raise UserError("Month not found")

        db.delete(month)
        db.commit()
        return month

    @staticmethod
    def get_all(db: Session, paginate, params):
        return paginate(db.query(MonthDetails).order_by(MonthDetails.id.desc()),
                        params,
                        transformer=lambda months: [MonthDetailsVo.model_validate(month) for month in months])

    @staticmethod
    def save(month: Month, db: Session):
        db.add(month)
        db.commit()
        db.refresh(month)
        return month

    @staticmethod
    def get_details(month_id: str, db: Session) -> MonthDetailsVo:
        month = db.query(MonthDetails).filter(MonthDetails.id == month_id).first()
        if not month:
            raise UserError("Month not found")
        return MonthDetailsVo.model_validate(month)
