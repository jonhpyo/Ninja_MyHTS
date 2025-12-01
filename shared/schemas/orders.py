from pydantic import BaseModel

class Order(BaseModel):
    id: int | None = None
    user_id: int
    account_id: int
    symbol: str
    side: str            # BUY / SELL
    qty: float
    order_type: str      # MARKET / LIMIT
    price: float | None = None
