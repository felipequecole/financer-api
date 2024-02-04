from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from src.schemas.bill_vo import BillUpdateVo, BillVo
from src.schemas.database import Bill


# todo return vo

class BillService:

    @staticmethod
    def save_all(db: Session, bills: list[Bill]) -> list[Bill]:
        db.add_all(bills)
        db.commit()
        [db.refresh(bill) for bill in bills]
        return bills

    @staticmethod
    def get_by_month(db: Session, month_id: str):
        return db.query(Bill).filter(Bill.month_id == month_id).all()

    @staticmethod
    def get_by_id(db: Session, id: str):
        db_id = UUID(id)
        bill = db.query(Bill).filter(Bill.id == db_id).first()
        return BillVo.model_validate(bill)

    @staticmethod
    def get_all_paginated(db: Session, paginate, params):
        return paginate(db.query(Bill).order_by(Bill.day),
                        params,
                        transformer=lambda bills: [BillVo.model_validate(bill) for bill in bills])

    @staticmethod
    def get_paginated_by_month(db: Session, month_id: str, paginate, params):
        return paginate(db.query(Bill).filter(Bill.month_id == month_id).order_by(Bill.day),
                        params,
                        transformer=lambda bills: [BillVo.model_validate(bill) for bill in bills])

    @staticmethod
    def delete(db: Session, id: str):
        db_id = UUID(id)
        bill = db.query(Bill).filter(Bill.id == db_id).first()
        db.delete(bill)
        db.commit()
        db.flush()

    @staticmethod
    def create(db: Session, month_id: str, new_bill: BillUpdateVo):
        db_bill = Bill(month_id=month_id, **new_bill.model_dump())
        db.add(db_bill)
        db.commit()
        db.refresh(db_bill)
        return BillVo.model_validate(db_bill)

    @staticmethod
    def update(db: Session, bill_id: str, updated_bill: BillUpdateVo):
        db_id = UUID(bill_id)
        current_bill = db.query(Bill).filter(Bill.id == db_id).first()
        for key, value in updated_bill.model_dump(exclude_unset=True).items():
            if (key == 'paid'):
                if (value and current_bill.paid_at is None):
                    setattr(current_bill, 'paid_at', datetime.now())
                elif (not value and current_bill.paid_at is not None):
                    setattr(current_bill, 'paid_at', None)
            setattr(current_bill, key, value)
        db.commit()
        db.refresh(current_bill)
        return BillVo.model_validate(current_bill)
