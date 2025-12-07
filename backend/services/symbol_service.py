from sqlalchemy.orm import Session
from backend.models.symbol_model import Symbol

def get_symbol_id(db: Session, symbol_code: str) -> int:
    row = db.query(Symbol).filter(Symbol.symbol_code == symbol_code).first()
    if not row:
        raise Exception(f"Unknown symbol: {symbol_code}")
    return row.symbol_id
