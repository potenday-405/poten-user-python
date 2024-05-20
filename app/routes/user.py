from fastapi import APIRouter, Request,Header, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database.settings import SessionLocal, engine
from app.services.user import UserService
from app.core.db import Engineconn
from app.models.user import UserSignup, UserSignupResponse

engine = Engineconn()
session = engine.create_session()

router = APIRouter()

def get_test_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/signup")
async def signup(user:UserSignup, db:Session = Depends(get_test_db), version: str = Header("1.0")) -> UserSignupResponse:
    """회원가입 api"""
    user_service = UserService(db)

    # 같은 이메일 존재하는지 체크
    is_existed = await user_service.check_existed_user(email=user.email)

    if is_existed:
        raise HTTPException(status_code=400, detail="Email already existed")

    # 없으면 회원가입
    await user_service.create_user(user)

    return UserSignupResponse(message="회원가입이 완료되었습니다.")