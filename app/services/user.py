from sqlalchemy.orm import Session
from app.database import models
from app.models.user import UserSignup, UserProfile, UserPassword
from sqlalchemy import insert, update
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

    async def check_validate_user(self, email, password):
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
            expire = datetime.utcnow() + timedelta(minutes=30)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    
    async def get_user_profile(self, user_id:str):

        user =  self.db.query(models.User).filter(models.User.user_id == user_id).first()

        return UserProfile(
            user_id = user_id,
            email = user.email,
            user_password = user.user_password,
            user_status = user.user_status,
            user_name = user.user_name,
            phone = user.phone,
            created_at = user.created_at,
            updated_at = user.updated_at,
        )
    
    async def verify_password(self, user_id:str, org_password:str):
        User = models.User
        print(user_id, "user_id")
        print(org_password, "org_password")
        user = self.db.query(User).filter(
            User.user_id == user_id,
            User.user_password == org_password
        ).first()

        return user

    async def modify_user_profile(
        self, 
        user_id:str, 
        new_password:str
    ):
        User = models.User

        self.db.execute(
            update(User)
            .where(User.user_id == user_id)
            .values(user_password=new_password)
        )

        self.db.commit()

    async def get_curr_id(self):
        user = self.db.query(models.User).order_by(models.User.created_at.desc()).first()
        return user.user_id
