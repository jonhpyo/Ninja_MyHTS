from sqlalchemy import Column, Integer, String, Numeric, TIMESTAMP, ForeignKey
from backend.db.database import Base
from sqlalchemy.orm import relationship


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.account_id"))
    symbol_id = Column(Integer, ForeignKey("symbols.symbol_id"))

    side = Column(String(10), nullable=False)  # BUY / SELL
    qty = Column(Numeric(20, 4), nullable=False)

    order_type = Column(String(10), default="MARKET")  # MARKET/LIMIT
    request_price = Column(Numeric(20, 8))
    exec_price = Column(Numeric(20, 8))

    status = Column(String(20), default="FILLED")
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

# 🔥 여기가 핵심!
    symbol = relationship("Symbol")