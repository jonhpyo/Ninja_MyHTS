from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.repositories.position_repo import PositionRepository

router = APIRouter(prefix="/positions", tags=["Positions"])

position_repo = PositionRepository()


@router.get("/{account_id}")
def get_positions(account_id: int, db: Session = Depends(get_db)):
    """
    계좌의 모든 포지션 조회
    """
    positions = db.query(position_repo.model).filter(
        position_repo.model. account_id == account_id
    ).all()
    return positions
