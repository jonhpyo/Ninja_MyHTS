import requests

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from collections import defaultdict

from backend.db.database import get_db
from backend.models.order_model import Order
from backend.models.symbol_model import Symbol
from backend.services.market.market_service import market_service

from backend.config.settings import BINANCE_DEPTH_URL

router = APIRouter(prefix="/orderbook", tags=["Orderbook"])

@router.get("/merged3/{symbol_code}/{account_id}")
def get_merged_orderbook_v3(symbol_code: str, account_id: int, db: Session = Depends(get_db)):

    symbol_code = symbol_code.upper()

    # 1) Binance depth
    depth = requests.get(
        BINANCE_DEPTH_URL, params={"symbol": symbol_code, "limit": 20}
    ).json()

    bin_bids = [(float(p), float(q)) for p, q in depth.get("bids", [])]
    bin_asks = [(float(p), float(q)) for p, q in depth.get("asks", [])]

    # 2) DB 전체 ORDER 집계
    orders = db.query(Order).filter(
        Order.symbol.has(symbol_code=symbol_code),
        Order.order_type == "LIMIT",
        Order.status == "OPEN"
    ).all()

    db_all = defaultdict(float)
    db_my = defaultdict(float)

    for o in orders:
        price = float(o.request_price)
        qty = float(o.qty)

        db_all[price] += qty

        if o.account_id == account_id:
            db_my[price] += qty

    def merge_side(bin_side, is_bid=True):
        merged = []
        for price, bin_qty in bin_side:
            all_qty = db_all.get(price, 0.0)
            my_qty = db_my.get(price, 0.0)

            merged.append({
                "price": price,
                "binance_qty": bin_qty,
                "db_all_qty": all_qty,
                "db_my_qty": my_qty
            })

        return merged

    return {
        "bids": merge_side(bin_bids, True),
        "asks": merge_side(bin_asks, False)
    }


@router.get("/{symbol_code}")
def get_merged_orderbook(symbol_code: str, db: Session = Depends(get_db)):
    """
    Binance WS Depth + 내부 주문을 합성해 오더북 생성
    """

    # 1) symbol_id 찾기
    symbol = (
        db.query(Symbol)
        .filter(Symbol.symbol_code == symbol_code.upper())
        .first()
    )
    if not symbol:
        raise HTTPException(404, "Symbol not found")
    symbol_id = symbol.symbol_id

    # 2) WS 기반 depth 가져오기 (⭐ 즉시 응답)
    cache = market_service.get_cache(symbol_code)
    if not cache:
        raise HTTPException(500, "No market cache")

    bin_bids = cache.get("depth_bids", [])
    bin_asks = cache.get("depth_asks", [])

    # 3) 내부 LIMIT OPEN 주문 가져오기
    orders = (
        db.query(Order)
        .filter(
            Order.symbol_id == symbol_id,
            Order.order_type == "LIMIT",
            Order.status == "OPEN",
        )
        .all()
    )



    my_bids = defaultdict(float)
    my_asks = defaultdict(float)

    for o in orders:
        price = float(o.request_price)
        qty = float(o.qty)
        print(price, qty, o.side)
        if o.side == "BUY":
            my_bids[price] += qty
        else:
            my_asks[price] += qty

    # 4) Binance depth 가격 레벨에 내부 수량 매핑
    out_bids = []
    for price, _ in bin_bids:
        qty = my_bids.get(price, 0.0)
        out_bids.append([price, qty])

    out_asks = []
    for price, _ in bin_asks:
        qty = my_asks.get(price, 0.0)
        out_asks.append([price, qty])

    # 5) mid price는 WS 기반으로 제공
    mid = cache.get("last")

    return {
        "bids": out_bids,
        "asks": out_asks,
        "mid": mid,
    }
