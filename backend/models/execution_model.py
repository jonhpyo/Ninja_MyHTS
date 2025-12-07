from sqlalchemy import Column, Integer, Numeric, String, ForeignKey, DateTime, func
from backend.db.database import Base


class Execution(Base):
    __tablename__ = "executions"

    exec_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"))
    account_id = Column(Integer, index=True)
    symbol_id = Column(Integer)
    side = Column(String(10))
    price = Column(Numeric(20, 8))
    qty = Column(Numeric(20, 4))
    fee = Column(Numeric(20, 4), default=0)
    exec_type = Column(String(20), default="TRADE")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
