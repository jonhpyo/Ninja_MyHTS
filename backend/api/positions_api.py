from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.models.position_model import Position
from backend.models.symbol_model import Symbol  # ← 반드시 정확한 경로로 import
                                             #   위치 알려주면 수정해 줄게

router = APIRouter(prefix="/positions", tags=["Positions"])


@router.get("/{account_id}")
def get_positions(account_id: int, db: Session = Depends(get_db)):
    """
    계좌의 모든 포지션 조회 → symbol 문자열 포함해서 반환
    """
    rows = (
        db.query(Position, Symbol.symbol_code)
        .join(Symbol, Position.symbol_id == Symbol.symbol_id)
        .filter(Position.account_id == account_id)
        .all()
    )

    result = []
    for pos, symbol_name in rows:
        qty = float(pos.qty)

        result.append(
            {
                "position_id": pos.position_id,
                "account_id": pos.account_id,
                "symbol_id": pos.symbol_id,
                "symbol": symbol_name,                      # 🔥 프론트에서 필요한 필드
                "side": "LONG" if qty >= 0 else "SHORT",   # qty로 방향 계산
                "qty": qty,
                "entry_price": float(pos.entry_price),
                "unrealized_pnl": float(pos.realized_pnl or 0),
                "updated_at": pos.updated_at.isoformat() if pos.updated_at else None,
            }
        )

    return result
