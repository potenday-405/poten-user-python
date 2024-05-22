from typing import Annotated, Union
from fastapi import APIRouter, Request,Header, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.database.settings import SessionLocal, engine, get_test_db
from app.services.user import UserService
from app.core.db import Engineconn
from app.models.user import *

router = APIRouter()

@router.post("/signup")
async def signup(user:UserSignup, db:Session = Depends(get_test_db), version: str = Header("1.0")) -> UserCommonResponse:
    """회원가입 api"""
    user_service = UserService(db)

    # 같은 이메일 존재하는지 체크
    is_existed = await user_service.check_existed_user(email=user.email)

    if is_existed:
        raise HTTPException(status_code=400, detail="Email already existed")

    # 없으면 회원가입
    await user_service.create_user(user)

    user_id = await user_service.get_curr_id()

    return UserCommonResponse(
        message="회원가입이 완료되었습니다.",
        data=str(user_id)
    )

@router.post("/login")
async def create_token(request:UserLogin, db:Session = Depends(get_test_db), version: str = Header("1.0")) -> UserToken:
    """로그인 시 accessToken 발행"""

    user_service = UserService(db)

    # 유효한 회원인지 체크
    is_validate = await user_service.check_validate_user(email=request.email, password=request.user_password)
    
    if not is_validate:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # accesstoken 발행
    access_token = user_service.create_access_token(data={"sub": is_validate.user_id})

    return UserToken(
        access_token=access_token,
        token_type="bearer"
    )
    

@router.get("/profile")
async def get_me(
    version: str = Header("1.0"), 
    user_id: str | None = Header(default=None), 
    db:Session = Depends(get_test_db)
) :
    """내 정보 조회"""
    
    user_service = UserService(db)
    return await user_service.get_user_profile(user_id)
    

@router.post("/profile")
async def modify_me(
    body : UserPassword,
    version: str = Header("1.0"), 
    user_id: Union[str, None] = Header(default=None), 
    db:Session = Depends(get_test_db)
) :
    """
        내 정보 수정

    
    """
    user_service = UserService(db)
    return await user_service.get_users()
    # 비밀번호 일치여부 체크
    # return await user_service.verify_password(user_id, body.org_password)

    # return await user_service.modify_user_profile(user_id, password)

# @router.get("/test")
# async def test():
#     """get 테스트용"""

#     return { "message" : "get test success!" }

# @router.post("/test")
# async def test():
#     """post 테스트용"""

#     return { "message" : "post test success!" }

# @router.put("/test")
# async def test():
#     """put 테스트용"""

#     return { "message" : "put test success!" }

# @router.delete("/test")
# async def test():
#     """put 테스트용"""

#     return { "message" : "delete test success!" }