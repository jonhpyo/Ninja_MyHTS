from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.schemas.order_schema import OrderCreate
from backend.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["Orders"])

order_service = OrderService()


@router.post("/market")
def place_market_order(payload: OrderCreate, db: Session = Depends(get_db)):
    """
    시장가 매수/매도 주문 → 즉시 체결
    """
    result = order_service.place_market_order(
        db=db,
        account_id=payload.account_id,
        symbol_code=payload.symbol,
        side=payload.side,
        qty=payload.qty
    )
    return result
