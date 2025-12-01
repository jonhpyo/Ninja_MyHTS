from fastapi import APIRouter, WebSocket
from starlette.websockets import WebSocketDisconnect
import asyncio

from backend.services.market.market_service import market_service

router = APIRouter(prefix="/ws", tags=["WebSocket"])

@router.websocket("/price/{symbol_code}")
async def price_stream(websocket: WebSocket, symbol_code: str):
    await websocket.accept()
    symbol = symbol_code.upper()

    try:
        while True:
            price = market_service.get_price(symbol)
            if price:
                await websocket.send_json(price)
            await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        print(f"[WS] Client disconnected: {symbol}")
    except Exception as e:
        print(f"[WS ERROR] {e}")
