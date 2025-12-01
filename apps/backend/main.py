from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI(title="MyHTS Backend", version="0.1.0")

class OrderRequest(BaseModel):
    user_id: int
    account_id: int
    symbol: str
    side: str          # "BUY" or "SELL"
    qty: float
    order_type: str = "MARKET"  # MARKET / LIMIT
    price: float | None = None

class OrderResponse(BaseModel):
    ok: bool
    order_id: int | None = None
    message: str | None = None

@app.get("/health")
async def health():
    return {"status": "ok", "service": "backend"}

@app.post("/orders", response_model=OrderResponse)
async def place_order(order: OrderRequest):
    # TODO: 이후 engine / risk / account_service 연동
    fake_order_id = 1
    return OrderResponse(
        ok=True,
        order_id=fake_order_id,
        message="order accepted (stub)"
    )

@app.get("/ping")
async def ping():
    return {"msg": "MyHTS backend alive"}
