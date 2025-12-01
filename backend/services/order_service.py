from sqlalchemy.orm import Session

from backend.repositories.order_repo import OrderRepository
from backend.repositories.execution_repo import ExecutionRepository
from backend.repositories.position_repo import PositionRepository
from backend.repositories.symbol_repo import SymbolRepository
from backend.repositories.account_repo import AccountRepository

from backend.services.position_service import position_service
from backend.services.account_service import account_service
from backend.services.market.market_service import market_service


class OrderService:

    def __init__(self):
        self.order_repo = OrderRepository()
        self.exec_repo = ExecutionRepository()
        self.position_repo = PositionRepository()
        self.symbol_repo = SymbolRepository()
        self.account_repo = AccountRepository()


    def place_market_order(self, db: Session,
                           account_id: int,
                           symbol_code: str,
                           side: str,
                           qty: float):

        account = self.account_repo.get(db, account_id)
        if not account:
            raise Exception("계좌 없음")

        symbol = self.symbol_repo.get_by_code(db, symbol_code)
        if not symbol:
            raise Exception("심볼 없음")

        # MarketService (싱글톤) 사용
        price_info = market_service.get_price(symbol_code)
        if not price_info:
            raise Exception(f"심볼 {symbol_code} 의 실시간 가격 없음(WS 연결 확인 필요)")

        exec_price = price_info["ask"] if side.upper() == "BUY" else price_info["bid"]

        order = self.order_repo.create(
            db,
            account_id=account_id,
            symbol_id=symbol.symbol_id,
            side=side,
            qty=qty,
            request_price=None
        )

        self.order_repo.update_exec_price(db, order, exec_price)

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

        position = position_service.handle_trade(
            db=db,
            account=account,
            symbol=symbol,
            side=side,
            qty=qty,
            exec_price=exec_price
        )

        account_service.update_after_trade(
            db=db,
            account=account,
            position=position,
            symbol=symbol
        )

        return {
            "ok": True,
            "order_id": order.order_id,
            "exec_price": float(exec_price),
            "position_qty": float(position.qty),
        }


order_service = OrderService()
