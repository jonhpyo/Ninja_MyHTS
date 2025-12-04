from sqlalchemy.orm import Session

from backend.repositories.position_repo import PositionRepository
from backend.models.account_model import Account
from backend.models.symbol_model import Symbol
from backend.models.position_model import Position
from backend.repositories.position_repo import position_repo

class PositionService:
    """
    선물 포지션 로직 담당 서비스
    """
    def __init__(self):
        self.position_repo = position_repo

    def handle_trade(
        self,
        db: Session,
        account: Account,
        symbol: Symbol,
        side: str,
        qty: float,
        exec_price: float,
    ) -> Position:
        """
        체결 1건을 포지션에 반영한다.

        side: "BUY" / "SELL"
        qty:  체결 수량(항상 양수)
        exec_price: 체결가
        """

        # 1) 기존 포지션 조회
        position = self.position_repo.get_by_account_symbol(
            db=db,
            account_id=account.account_id,
            symbol_id=symbol.symbol_id
        )
        signed_qty = qty if side.upper() == "BUY" else -qty
        exec_price_f = float(exec_price)
        multiplier = float(symbol.multiplier)

        # 포지션이 없으면 새로 생성 (신규 진입)
        if position is None:
            position = self.position_repo.create(
                db=db,
                account_id=account.account_id,
                symbol_id=symbol.symbol_id,
                qty=signed_qty,
                entry_price=exec_price_f,
            )
            return position

        # 기존 포지션 정보
        old_qty = float(position.qty or 0.0)
        old_entry = float(position.entry_price or exec_price_f)
        old_realized = float(position.realized_pnl or 0.0)

        # ---------------------------
        # Case 1: 기존 0 or 같은 방향 (증가)
        # ---------------------------
        if old_qty == 0 or (old_qty > 0 and signed_qty > 0) or (old_qty < 0 and signed_qty < 0):
            new_qty = old_qty + signed_qty

            # 가중 평균 단가
            new_entry_price = (old_qty * old_entry + signed_qty * exec_price_f) / new_qty

            position = self.position_repo.update(
                db=db,
                position=position,
                qty=new_qty,
                entry_price=new_entry_price,
                realized_pnl=old_realized,
            )
            return position

        # ---------------------------
        # Case 2: 반대 방향 (청산 / 반전)
        # ---------------------------
        # 청산되는 수량
        close_qty = min(abs(old_qty), abs(signed_qty))

        # 롱 → 숏 청산 (SELL 체결로 롱 감소)
        realized_pnl_delta = 0.0
        if old_qty > 0 and signed_qty < 0:
            # 롱 포지션 청산: (exit - entry) * 수량 * multiplier
            realized_pnl_delta = (exec_price_f - old_entry) * close_qty * multiplier

        # 숏 → 롱 청산 (BUY 체결로 숏 감소)
        elif old_qty < 0 and signed_qty > 0:
            # 숏 포지션 청산: (entry - exit) * 수량 * multiplier
            realized_pnl_delta = (old_entry - exec_price_f) * close_qty * multiplier

        # 남는 수량 (완전 청산 또는 반전)
        remaining_qty = old_qty + signed_qty  # 부호 포함

        if abs(remaining_qty) < 1e-10:
            # 완전 청산 → qty = 0으로 유지 (기록용)
            new_qty = 0.0
            # entry_price는 의미 없지만 그냥 두거나 exec_price로 맞춰도 됨
            new_entry_price = exec_price_f
        else:
            # 일부 청산 + 남은 포지션
            new_qty = remaining_qty
            # 남은 포지션이 원래 방향과 같으면 entry_price 그대로,
            # 반전(롱→숏 또는 숏→롱)이면 새 방향 기준으로 entry_price = 이번 체결가
            if (old_qty > 0 and remaining_qty > 0) or (old_qty < 0 and remaining_qty < 0):
                new_entry_price = old_entry
            else:
                new_entry_price = exec_price_f

        new_realized = old_realized + realized_pnl_delta

        position = self.position_repo.update(
            db=db,
            position=position,
            qty=new_qty,
            entry_price=new_entry_price,
            realized_pnl=new_realized,
        )

        return position

position_service = PositionService()