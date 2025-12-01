from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.repositories.execution_repo import ExecutionRepository

router = APIRouter(prefix="/executions", tags=["Executions"])
exec_repo = ExecutionRepository()


@router.get("/{account_id}")
def get_executions(account_id: int, db: Session = Depends(get_db)):
    return exec_repo.get_by_account(db, account_id)
