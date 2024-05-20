import os
from fastapi import APIRouter, Request,Header, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional
import httpx
import secrets
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.db import Engineconn
from app.models.user import UserSignup, UserInDB, UserToken, User
from app.database.schema import TestUser
import uuid

engine = Engineconn()
session = engine.create_session()

router = APIRouter()

# 인증 util 함수 추후에 분리 --------------

# JWT 설정

# 비밀번호 암호화 및 검증을 위한 클래스
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 사용자 인증 엔드포인트에서 필요함.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_password_hash(password):
    return pwd_context.hash(password)

def create_user(user:UserSignup):
    hashed_password = get_password_hash(user.password)
    db_user = UserInDB(**user.dict(), hashed_password=hashed_password)
    fake_users_db[user.email] = db_user
    return db_user

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# JWT 토큰 생성 함수
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# 새로운 토큰 발급 함수
def create_new_token(email: str):
    expiration = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": email, "exp": expiration}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

# DB에 해당 유저가 있는 지 확인하는 함수
def get_user(db, user_name:str):
    if user in db:
        user_dict = db[user_name]
        return UserInDB(*user_dict)

def authenticate_user(fake_users_db, user_name:str, password):
    user = get_user(fake_users_db, user_name)
    if not user:
        return False
    if not get_password_hash(password) == user.hashed_password:
        return False
    return user

def get_user(db: dict, email: str):
    if email in db:
        user_data = db[email]
        return User(username=user_data["username"], email=user_data["email"])
    return None

# 토큰 검증 함수
async def get_current_user(token:str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401, 
        detail="Can not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithm=ALGORITHM)
        email : str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = email
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, token_data)
    if user is None:
        raise credentials_exception
    return user

# 토큰 검증 API
async def validate_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        if email not in fake_users_db:
            raise HTTPException(status_code=401, detail="User not found")
        
        # 만료 시간 확인
        expiration = payload.get("exp")
        if expiration is None or datetime.utcnow() > datetime.fromtimestamp(expiration):
            # 토큰이 만료되었으면 새로운 토큰 발급
            new_token = create_new_token(email)
            return {"valid": False, "new_token": new_token}

        return {"valid": True, "username": fake_users_db[email]["username"]}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def generate_uuid():
    return str(uuid.uuid4()) + current_timestamp

@router.post("/signup")
async def signup(user:UserSignup):
    """
    회원가입 api
    """
    # 새로운 레코드 생성
    # new_user = TestUser(
    #     email=user.email,
    #     user_password=get_password_hash(user.password),
    #     user_name=user.name,
    #     phone=user.phone,
    #     user_status="act"
    # )

    # # 세션에 추가
    # session.add(new_user)

    # # 변경 내용을 커밋하여 DB에 반영
    # session.commit()

    # 같은 이메일 존재하는지 체크
    example = session.query(TestUser).all()
    return example

    # if user.email in fake_users_db:
    #     raise HTTPException(status_code=400, detail="Email already existed")
    
    created_user = create_user(user)
    return created_user

@router.post("/login", response_model=UserToken)
async def login_for_access_token(email: str, password: str):
    """
        로그인 시 accessToken발생
    """
    user = fake_users_db.get(email)
    
    if not user or not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    access_token = create_access_token(
        data={"sub": email}, expires_delta=access_token_expires
    )
    
    return UserToken(
        access_token=access_token,
        token_type="bearer"
    )

# 내 정보 조회
@router.get("/me", )
async def read_user_me(current_user:User = Depends(get_current_user)):
    return current_user