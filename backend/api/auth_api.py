from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.services.auth_service import auth_service
from backend.db.database import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])

class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    account_id: int


@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest, db: Session = Depends(get_db)):
    # 🔹 JSON body 로 들어온 값 사용
    user, token, account_id = auth_service.login(
        db, payload.email, payload.password
    )

    return LoginResponse(
        access_token=token,
        user_id=user.user_id,
        account_id=account_id,
    )
