import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.db.database import SessionLocal
from backend.repositories.position_repo import PositionRepository
from backend.repositories.account_repo import AccountRepository
from backend.services.account_service import account_service
from backend.services.market.market_service import market_service
from backend.services.ws_broadcast import broadcast_manager

router = APIRouter()

pos_repo = PositionRepository()
acc_repo = AccountRepository()


@router.websocket("/ws/account/{account_id}")
async def account_ws(websocket: WebSocket, account_id: int):
    await websocket.accept()
    print(f"[WS] Account WS Connected → {account_id}")
    await broadcast_manager.connect(account_id, websocket)

    try:
        while True:
            await asyncio.sleep(0.2)

            db = SessionLocal()

            # =======================================
            # ① 계좌 먼저 가져오기  ★ 매우 중요
            # =======================================
            account = acc_repo.get(db, account_id)

            # ================================
            # ① 포지션 목록 가져오기
            # ================================
            positions = pos_repo.get_by_account(db, account_id)
            pos_rows = []

            for p in positions:
                price_info = market_service.get_price(p.symbol.symbol_code)
                last_price = price_info.get("last") if price_info else None
                multiplier = float(p.symbol.multiplier)

                qty = float(p.qty or 0)
                entry_price = float(p.entry_price or 0)

                # ---- 미실현손익 계산 ----
                if qty == 0 or last_price is None:
                    upnl = 0.0
                else:
                    if qty > 0:  # 롱
                        upnl = (last_price - entry_price) * qty * multiplier
                    else:  # 숏
                        upnl = (entry_price - last_price) * abs(qty) * multiplier

                liq = account_service.calc_liquidation_price(p, account, p.symbol)

                pos_rows.append({
                    "symbol": p.symbol.symbol_code,
                    "side": ("LONG" if float(p.qty) > 0 else "SHORT" if float(p.qty) < 0 else ""),
                    "qty": qty,
                    "entry_price": entry_price,
                    "realized_pnl": float(p.realized_pnl or 0),
                    "unrealized_pnl": upnl,  # ⭐ 드디어 포함됨!
                    "current_price": last_price,
                    "liq_price": liq
                })

            # ================================
            # ② 계좌 정보 가져오기
            # ================================
            account = acc_repo.get(db, account_id)
            account_row = {
                "balance": float(account.balance),
                "margin_used": float(account.margin_used),
                "margin_available": float(account.margin_available),
                "pnl_realized": float(account.pnl_realized),
                "pnl_unrealized": float(account.pnl_unrealized),
            }

            db.close()

            # ================================
            # ③ 클라이언트로 Push
            # ================================
            await websocket.send_json({
                "type": "account_update",
                "positions": pos_rows,
                "account": account_row
            })

    except WebSocketDisconnect:
        print(f"[WS] Account WS Disconnected → {account_id}")
        broadcast_manager.disconnect(account_id, websocket)

