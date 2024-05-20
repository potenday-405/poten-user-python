from sqlalchemy.orm import Session
from app.database import models
from app.models.user import UserSignup
from sqlalchemy import insert
from app.utils.user import get_hashed_password
from jose import JWTError, jwt
from typing import Optional
from datetime import datetime, timedelta
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM

class UserService():
    def __init__(self, db:Session):
        self.db = db

    async def check_existed_user(self, email:str):
        """회원가입 시 email을 통해 이미 가잆된 사용자가 있는지 반환

        :return : 유저 정보
        """
        User = models.User
        user = self.db.query(User).filter(User.email == email).first()
        return user

    async def create_user(self, user:UserSignup):
        """회원가입"""
        self.db.execute(
            insert(models.User).values(
            **user.dict(),
            # password=get_hashed_password(user.password),
            user_status='act'
        ))

        self.db.commit()
        
        return user

    async def check_validate_user(self, email:str, password):
        """이메일로 사용자 조회"""
        User = models.User
        user = self.db.query(User).filter(
            User.email == email,
            User.user_password == password
        ).first()
        return user

    async def get_users(self):
        return self.db.query(models.User).all()

    #TODO auth쪽은 따로 분리할 것
    # JWT 토큰 생성 함수 
    def create_access_token(self, data: dict):

        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt