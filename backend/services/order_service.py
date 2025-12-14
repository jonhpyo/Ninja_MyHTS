import asyncio

from sqlalchemy.orm import Session

from backend.repositories.order_repo import OrderRepository
from backend.repositories.execution_repo import ExecutionRepository
from backend.repositories.position_repo import PositionRepository
from backend.repositories.symbol_repo import SymbolRepository
from backend.repositories.account_repo import AccountRepository

from backend.services.position_service import position_service
from backend.services.account_service import account_service
from backend.services.market.market_service import market_service

from backend.api.trades_ws_api import broadcast_trade



class OrderService:

    def __init__(self):
        self.order_repo = OrderRepository()
        self.exec_repo = ExecutionRepository()
        self.position_repo = PositionRepository()
        self.symbol_repo = SymbolRepository()
        self.account_repo = AccountRepository()

    def place_market_order(
            self,
            db: Session,
            account_id: int,
            symbol_code: str,
            side: str,
            qty: float
    ):
        account = self.account_repo.get(db, account_id)
        if not account:
            raise Exception("계좌 없음")

        symbol = self.symbol_repo.get_by_code(db, symbol_code)
        if not symbol:
            raise Exception("심볼 없음")

        # 실시간 가격
        price_info = market_service.get_price(symbol_code)
        if not price_info:
            raise Exception(f"{symbol_code} 실시간 가격 없음")

        exec_price = (
            price_info["ask"]
            if side.upper() == "BUY"
            else price_info["bid"]
        )

        # 주문 생성 (Market)
        order = self.order_repo.create(
            db=db,
            account_id=account_id,
            symbol_id=symbol.symbol_id,
            side=side,
            qty=qty,
            request_price=None
        )

        # execution 생성
        execution = self.exec_repo.create(
            db=db,
            order_id=order.order_id,
            account_id=account.account_id,
            symbol_id=symbol.symbol_id,
            side=side,
            price=exec_price,
            qty=qty,
            fee=0.0
        )

        # position 갱신
        position = position_service.handle_trade(
            db=db,
            account=account,
            symbol=symbol,
            side=side,
            qty=qty,
            exec_price=exec_price
        )

        # 계좌 갱신
        account_service.update_after_trade(
            db=db,
            account=account,
            position=position,
            symbol=symbol
        )

        # 주문 상태 FILLED
        self.order_repo.mark_filled(db, order)

        # ==================================================
        # 🔥🔥🔥 Time & Sales WS 브로드캐스트
        # ==================================================
        trade_data = {
            "type": "trade",
            "symbol": symbol.symbol_code,
            "price": float(exec_price),
            "qty": float(qty),
            "side": side,
            "ts": execution.created_at.isoformat(),
        }

        loop = asyncio.get_event_loop()
        loop.call_soon_threadsafe(
            lambda: asyncio.create_task(broadcast_trade(trade_data))
        )

        return {
            "ok": True,
            "order_id": order.order_id,
            "exec_price": float(exec_price),
            "position_qty": float(position.qty),
        }

    def place_limit_order(
            self,
            db: Session,
            account_id: int,
            symbol_code: str,
            side: str,
            qty: float,
            price: float
    ):
        """지정가 주문 생성 → 오더북에 쌓이고 체결되지 않음"""

        account = self.account_repo.get(db, account_id)
        if not account:
            raise Exception("계좌 없음")

        symbol = self.symbol_repo.get_by_code(db, symbol_code)
        if not symbol:
            raise Exception("심볼 없음")

        # order 생성 (status = OPEN)
        order = self.order_repo.create_limit(
            db=db,
            account_id=account_id,
            symbol_id=symbol.symbol_id,
            side=side,
            qty=qty,
            price=price
        )

        return {
            "ok": True,
            "order_id": order.order_id,
            "request_price": float(order.request_price),
            "status": order.status
        }

    # ------------------------------
    # OPEN LIMIT ORDERS 조회
    # ------------------------------
    # backend/services/order_service.py
    def get_open_orders(self, db: Session, account_id: int):
        orders = self.order_repo.get_open_orders(db, account_id)

        return [
            {
                "order_id": o.order_id,
                "symbol": o.symbol.symbol_code,  # ← join 후 정상 동작
                "side": o.side,
                "price": float(o.request_price or 0),
                "qty": float(o.qty),
                "status": o.status,
                "created_at": o.created_at.isoformat() if o.created_at else "",
            }
            for o in orders
        ]

    def cancel_orders(self, db: Session, order_ids: []):
        return self.order_repo.cancel_orders(db, order_ids)

    def execute_limit_order(self, db, order, exec_price):
        account = self.account_repo.get(db, order.account_id)
        symbol = order.symbol  # relationship

        # executions 생성
        execution = self.exec_repo.create(
            db=db,
            order_id=order.order_id,
            account_id=order.account_id,
            symbol_id=order.symbol_id,
            side=order.side,
            price=exec_price,
            qty=order.qty,
            fee=0.0
        )

        # position 업데이트
        position = position_service.handle_trade(
            db=db,
            account=account,
            symbol=symbol,
            side=order.side,
            qty=order.qty,
            exec_price=exec_price
        )

        # 계좌 업데이트
        account_service.update_after_trade(
            db=db,
            account=account,
            position=position,
            symbol=symbol
        )

        # 주문 상태 = FILLED
        self.order_repo.mark_filled(db, order)

        # ==================================================
        # 🔥🔥🔥 Time & Sales WS 브로드캐스트 (핵심)
        # ==================================================
        trade_data = {
            "type": "trade",
            "symbol": symbol.symbol_code,
            "price": float(exec_price),
            "qty": float(order.qty),
            "side": order.side,
            "ts": execution.created_at.isoformat(),
        }

        loop = asyncio.get_event_loop()
        loop.call_soon_threadsafe(
            lambda: asyncio.create_task(broadcast_trade(trade_data))
        )

        return execution


order_service = OrderService()
