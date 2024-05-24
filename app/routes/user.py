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
    """회원가입 api

        user_name : 이름
        
        email : 이메일주소

        user_password : 비밀번호
        
        phone : 전화번호
    """
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
    """
        로그인 시 accessToken 발행

        email : 이메일 주소
        
        user_password : 비밀번호
    """

    user_service = UserService(db)

    # 유효한 회원인지 체크
    is_validate = await user_service.check_validate_user(email=request.email, password=request.user_password)
    
    if not is_validate:
        raise HTTPException(
            status_code=401,
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
    request:Request,
    db:Session = Depends(get_test_db)
) :
    """내 정보 조회"""
    headers = request.headers
    user_id = headers.get("user_id")

    user_service = UserService(db)
    return await user_service.get_user_profile(user_id)
    

@router.put("/profile")
async def modify_me(
    body : UserPassword,
    request:Request,
    db:Session = Depends(get_test_db)
) :
    """
        내 정보 수정

        org_password : 기존 비밀번호
        
        new_password : 나중 비밀번호

    """
    headers = request.headers
    user_id = headers.get("user_id")

    user_service = UserService(db)

    # 현재 비밀번호가 유효한지 체크
    is_valid_password = await user_service.verify_password(user_id, body.org_password)

    if not is_valid_password:
        raise HTTPException(status_code=400, detail="Original Password is not valid")

    # 유효할 경우, user_id로 password 업데이트 
    await user_service.modify_user_profile(user_id, body.new_password)

    return UserCommonResponse(
        message="정보수정이 완료되었습니다.",
        data=str(user_id)
    )


@router.post("/score")
async def get_sum_score(
    request : Request,
    body:CalcUserScore,
    db:Session = Depends(get_test_db)
) -> UserCommonResponse:
    """
        축의금 등록/수정/삭제에 의해 변동된 점수를 조회.

        method : 등록(POST) / 수정(PUT) / 삭제(DELETE)
        
        is_attended : 1(참석) / 0(불참)
    """

    headers = request.headers
    user_id = headers.get("user_id")

    user_service = UserService(db)

    # 현재 회원의 score 조회
    prev_score = await user_service.get_score(user_id)
    new_score = await user_service.calculate_user_score(prev_score, body)
    await user_service.modify_user_score(user_id, prev_score, new_score, body.invitation_type)

    return UserCommonResponse(
        message="회원의 점수가 변경되었습니다.",
        data={
            "prev_score" : prev_score,
            "new_score" : new_score
        }
    )

@router.get("/score")
async def get_user_score(
    request : Request,
    db:Session = Depends(get_test_db)
):
    """회원 점수 조회"""

    headers = request.headers
    user_id = headers.get("user_id")

    user_service = UserService(db)

    # 현재 회원의 score 조회
    return await user_service.get_score(user_id)

@router.post("/test")
async def get_sum_score(
    request : Request,
    body:CalcUserScore
) :

    headers = request.headers
    user_id = headers.get("user_id")

    return user_id