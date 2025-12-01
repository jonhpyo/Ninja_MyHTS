from sqlalchemy.orm import Session
from backend.models.execution_model import Execution


class ExecutionRepository:

    def create(self, db: Session, order_id: int, account_id: int,
               symbol_id: int, side: str, price: float, qty: float, fee: float = 0):

        exec_record = Execution(
            order_id=order_id,
            account_id=account_id,
            symbol_id=symbol_id,
            side=side,
            price=price,
            qty=qty,
            fee=fee
        )

        db.add(exec_record)
        db.commit()
        db.refresh(exec_record)
        return exec_record

    def get_by_account(self, db: Session, account_id: int):
        return db.query(Execution).filter(Execution.account_id == account_id).all()

    def get_by_order(self, db: Session, order_id: int):
        return db.query(Execution).filter(Execution.order_id == order_id).all()
