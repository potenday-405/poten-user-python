from fastapi import APIRouter, Request,Header, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.database.settings import SessionLocal, engine
from app.services.user import UserService
from app.core.db import Engineconn
from app.models.user import UserSignup, UserSignupResponse, UserToken

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

@router.post("/login")
async def create_token(email:str, password:str, db:Session = Depends(get_test_db), version: str = Header("1.0")) -> UserToken:
    """로그인 시 accessToken 발행"""

    user_service = UserService(db)

    # 유효한 회원인지 체크
    is_validate = await user_service.check_validate_user(email=email, password=password)
    if not is_validate:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # accesstoken 발행
    access_token = user_service.create_access_token(data={"sub": email})

    return UserToken(
        access_token=access_token,
        token_type="bearer"
    )
    
    
