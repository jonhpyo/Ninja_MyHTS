from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.repositories.account_repo import AccountRepository

router = APIRouter(prefix="/accounts", tags=["Accounts"])
account_repo = AccountRepository()


@router.get("/{account_id}")
def get_account(account_id: int, db: Session = Depends(get_db)):
    account = account_repo.get(db, account_id)
    if not account:
        return {"error": "Account not found"}
    return account
