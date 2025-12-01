from sqlalchemy import Column, Integer, String, Numeric, TIMESTAMP, ForeignKey
from backend.db.database import Base


class Execution(Base):
    __tablename__ = "executions"

    exec_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"))
    account_id = Column(Integer, ForeignKey("accounts.account_id"))
    symbol_id = Column(Integer, ForeignKey("symbols.symbol_id"))

    side = Column(String(10))
    price = Column(Numeric(20, 8))
    qty = Column(Numeric(20, 4))
    fee = Column(Numeric(20, 4), default=0)

    exec_type = Column(String(20), default="TRADE")
    created_at = Column(TIMESTAMP)
