from backend.repositories.base_repo import BaseRepository
from backend.models.position_model import Position
from sqlalchemy.orm import Session


class PositionRepository(BaseRepository):
    model = Position

    def get_by_account(self, db, account_id: int):
        return db.query(self.model).filter(self.model.account_id == account_id).all()

    def get_by_account_symbol(self, db: Session, account_id: int, symbol_id: int):
        return (
            db.query(Position)
            .filter(
                Position.account_id == account_id,
                Position.symbol_id == symbol_id
            )
            .first()
        )

    def update(self, db: Session, position: Position, **kwargs):
        for key, value in kwargs.items():
            setattr(position, key, value)
        db.commit()
        db.refresh(position)
        return position
