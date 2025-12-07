from sqlalchemy.orm import Session, joinedload
from backend.models.order_model import Order
from backend.models.symbol_model import Symbol

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

    def create_limit(self, db: Session, account_id: int, symbol_id: int,
                     side: str, qty: float, price: float):
        order = Order(
            account_id=account_id,
            symbol_id=symbol_id,
            side=side,
            qty=qty,
            request_price=price,
            status="OPEN",
            order_type="LIMIT"
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

    # ---------------------------------------------------------
    # READ: 계좌의 OPEN 상태 LIMIT 주문 조회
    # ---------------------------------------------------------
    def get_open_orders(self, db: Session, account_id: int):
        orders = (
            db.query(Order)
            .join(Symbol, Order.symbol_id == Symbol.symbol_id)
            .options(joinedload(Order.symbol))
            .filter(Order.account_id == account_id, Order.status == "OPEN")
            .order_by(Order.order_id.desc())
            .all()
        )
        return orders

    # ---------------------------------------------------------
    # CANCEL: 주문 취소
    # ---------------------------------------------------------
    def cancel_orders(self, db: Session, order_ids: list[int]):
        """
        여러 주문을 한 번에 취소한다.
        조건:
        - OPEN 상태인 주문만 취소 가능
        """
        cancelled = (
            db.query(Order)
            .filter(
                Order.order_id.in_(order_ids),
                Order.status == "OPEN"
            )
            .all()
        )

        for o in cancelled:
            o.status = "CANCELLED"

        db.commit()
        return [o.order_id for o in cancelled]
