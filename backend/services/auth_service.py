# backend/services/auth_service.py
import bcrypt
import jwt
from sqlalchemy.orm import Session
from fastapi import HTTPException

from backend.repositories.user_repo import user_repo
from backend.repositories.account_repo import account_repo


class AuthService:
    SECRET_KEY = "CHANGE_ME_SECRET"   # TODO: 환경변수/설정에서 가져오도록 변경 권장
    ALGORITHM = "HS256"

    def login(self, db: Session, email: str, password: str):
        # 1) 사용자 조회
        user = user_repo.get_by_email(db, email)
        if not user:
            # FastAPI가 JSON으로 내려줄 수 있도록 HTTPException 사용
            raise HTTPException(status_code=400, detail="Invalid email or password")

        # 2) 비밀번호 체크 (users.password_hash 기준)
        # users 테이블: password_hash 컬럼 사용 중 (bcrypt 해시)
        if not bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
            raise HTTPException(status_code=400, detail="Invalid email or password")

        # 3) JWT 발급
        payload = {
            "user_id": user.user_id,
            "email": user.email,
        }
        token = jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)

        # 4) 기본 계좌 조회 (없으면 에러)
        account = account_repo.get_primary_account(db, user.user_id)
        if not account:
            raise HTTPException(status_code=400, detail="No account for this user")

        # 5) auth_api에서 언급된 형태로 반환
        return user, token, account.account_id


auth_service = AuthService()
