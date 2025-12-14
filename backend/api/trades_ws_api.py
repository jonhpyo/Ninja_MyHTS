# backend/ws/trades_ws.py
import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

# symbol별 접속자 관리
trade_clients: dict[str, set[WebSocket]] = {}


@router.websocket("/ws/trades/{symbol}")
async def trades_ws(websocket: WebSocket, symbol: str):
    await websocket.accept()
    symbol = symbol.upper()

    if symbol not in trade_clients:
        trade_clients[symbol] = set()

    trade_clients[symbol].add(websocket)
    print(f"[TRADES WS] Connected: {symbol}")

    try:
        # 🔥 수신 대기 ❌
        while True:
            await asyncio.sleep(3600)  # 연결 유지용
    except WebSocketDisconnect:
        trade_clients[symbol].remove(websocket)
        print(f"[TRADES WS] Disconnected: {symbol}")


async def broadcast_trade(trade: dict):
    """
    trade = {
        symbol, price, qty, side, ts
    }
    """
    print("[BROADCAST_TRADE CALL]", trade)

    symbol = trade["symbol"].upper()

    if symbol not in trade_clients:
        print("[BROADCAST_TRADE] no clients for", symbol)
        return

    dead = []

    for ws in trade_clients[symbol]:
        try:
            await ws.send_text(json.dumps(trade))
        except:
            dead.append(ws)

    for ws in dead:
        trade_clients[symbol].remove(ws)

