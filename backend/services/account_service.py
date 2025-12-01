from sqlalchemy.orm import Session
from backend.repositories.account_repo import AccountRepository
from backend.services.market.market_service import market_service
from backend.models.account_model import Account
from backend.models.symbol_model import Symbol
from backend.models.position_model import Position

class AccountService:

    def __init__(self):
        self.account_repo = AccountRepository()


    # ----------------------------------------------------
    #  실현손익(RPnL) + 미실현손익(UPnL) + 증거금 업데이트
    # ----------------------------------------------------
    def update_after_trade(
        self,
        db: Session,
        account: Account,
        position: Position,
        symbol: Symbol
    ):
        """
        주문 체결 후 계좌 상태를 갱신한다.
        포지션이 변한 뒤:
        - 실현손익 반영
        - 미실현손익 재 계산
        - 증거금 계산
        """

        # ============================
        # 1) 실현손익(RPnL) 반영
        # ============================
        realized_pnl = float(position.realized_pnl or 0.0)

        # account.pnl_realized는 누적 값
        pnl_realized_account = float(account.pnl_realized or 0.0)
        new_total_realized = realized_pnl

        # balance에도 실현손익 반영
        balance = float(account.balance or 0.0)
        new_balance = balance + (realized_pnl - pnl_realized_account)

        # ============================
        # 2) 미실현손익(UPnL) 계산
        # ============================
        # 포지션이 없는 경우 qty = 0 이면 UPNL은 0
        qty = float(position.qty or 0.0)
        entry_price = float(position.entry_price or 0.0)

        upnl = 0.0

        if qty != 0:
            price_info = market_service.get_price(symbol.symbol_code)
            if not price_info:
                raise Exception("실시간 가격 없음 → MarketService WS 문제")

            current_price = float(price_info["bid"] if qty < 0 else price_info["ask"])
            multiplier = float(symbol.multiplier)

            # 롱
            if qty > 0:
                upnl = (current_price - entry_price) * qty * multiplier
            # 숏
            else:
                upnl = (entry_price - current_price) * abs(qty) * multiplier

        # ============================
        # 3) 사용 증거금(Margin Used)
        # ============================
        if qty == 0:
            margin_used = 0.0
        else:
            margin_used = abs(qty) * float(symbol.initial_margin)

        # ============================
        # 4) 여유 증거금(Margin Available)
        # ============================
        margin_available = new_balance + upnl - margin_used

        # ============================
        # 5) 계좌 업데이트
        # ============================
        updated_account = self.account_repo.update_balance(
            db=db,
            account=account,
            balance=new_balance,
            pnl_realized=new_total_realized,
            pnl_unrealized=upnl,
            margin_used=margin_used,
            margin_available=margin_available
        )

        return updated_account

account_service = AccountService()