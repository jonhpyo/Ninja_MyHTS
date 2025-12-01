from sqlalchemy.orm import Session
from backend.models.order_model import Order


class OrderRepository:

    def get(self, db: Session, order_id: int):
        return db.query(Order).filter(Order.order_id == order_id).first()

    def get_by_account(self, db: Session, account_id: int):
        return db.query(Order).filter(Order.account_id == account_id).all()

    def create(self, db: Session, account_id: int, symbol_id: int,
               side: str, qty: float, request_price=None):

        order = Order(
            account_id=account_id,
            symbol_id=symbol_id,
            side=side,
            qty=qty,
            request_price=request_price,
            order_type="MARKET",     # 현재는 MARKET 고정
            status="FILLED"          # 즉시 체결 HTS 구조
        )

        db.add(order)
        db.commit()
        db.refresh(order)
        return order

    def update_exec_price(self, db: Session, order: Order, price: float):
        order.exec_price = price
        db.commit()
        db.refresh(order)
        return order
