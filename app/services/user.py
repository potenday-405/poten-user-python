from sqlalchemy.orm import Session
from sqlalchemy import insert, update
from sqlalchemy.exc import OperationalError
from app.database import models
from app.models.user import UserSignup, UserProfile, UserPassword, CalcUserScore
from jose import JWTError, jwt
from typing import Optional
from datetime import datetime, timedelta
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_SECRET_KEY, SECRET_KEY, ALGORITHM
from fastapi import HTTPException, status

import bcrypt

class UserService():
    def __init__(self, db:Session):
        self.db = db

    @staticmethod
    def get_encrypted_password(password:str):
        """비밀번호 암호화 해서 return하는 메소드."""
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(password:str, encrypted_password:str):
        """비밀번호 유효성 검사"""
        return bcrypt.checkpw(password.encode('utf-8'), encrypted_password.encode('utf-8'))

    async def check_existed_user(self, email:str):
        """회원가입 시 email을 통해 이미 가잆된 사용자가 있는지 반환

        :return : 유저 정보
        """
        User = models.User
        user = self.db.query(User).filter(User.email == email).first()
        return user

    async def create_user(self, user:UserSignup):
        """회원가입"""

        self.db.execute(insert(models.User).values({
            **user.dict(),
            "user_password" :self.get_encrypted_password(user.user_password),
            "user_status" : "act"
        }))

        self.db.commit()
        
        return user

    async def check_validate_user(self, email):
        """이메일로 사용자 조회"""
        User = models.User
        user = self.db.query(User).filter(User.email == email).first()
        return user
    
    def check_validate_password(self, password:str, encrypted_password:str):
        """이메일로 사용자 조회"""
        return bcrypt.checkpw(password.encode('utf-8'), encrypted_password.encode('utf-8'))

    async def get_users(self):
        return self.db.query(models.User).all()

    #TODO auth쪽은 따로 분리할 것
    # JWT 토큰 생성 함수 
    def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=2)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def create_refresh_token(self, data:dict ):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
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

        # TODO update용 쿼리 실행함수 따로 분리할 것 🚨
        try:
            self.db.execute(
                update(User)
                .where(User.user_id == user_id)
                .values(user_password=new_password)
            )

            self.db.commit()
        except OperationalError as e:
            error_msg = "Failed to modify user profile."
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_msg)

    async def get_curr_id(self):
        user = self.db.query(models.User).order_by(models.User.created_at.desc()).first()
        return user.user_id

    async def get_score(self, user_id:str):
        score_info = self.db.query(models.Score).filter(models.Score.user_id == user_id).first()
        if score_info:
            return score_info.score
        else:
            return 0

    async def calculate_user_score(self, prev_score:int, body:CalcUserScore):

        attended = { "1" : 40,"2" : 15,"3" : 9, "4" : 6, "5" : 3 }
        non_attended = { "1" : 20,"2" : 5, "3" : 3, "4" : 2, "5" : 1 }
        record = { "1" : 40,"2" : 15,"3" : 9, "4" : 6, "5" : 3 }

        # 각 등급별 score 부여처리
        if prev_score <= 300:
            grade = "1"
        elif 300 < grade <= 450:
            grade = "2"
        elif 450 < grade <= 585:
            grade = "3"
        elif 585 < grade <= 772:
            grade = "4"
        else:
            grade = "5"

        method, is_attended = body.method, body.is_attended

        attended_score = attended.get(f"{grade}") if is_attended == 1 else int(non_attended.get(f"{grade}"))

        if method == "POST":
            method_score = record.get(f"{grade}")
            return method_score + attended_score + prev_score
        elif method == "DELETE":
            method_score = -int(record.get(f"{grade}"))
            return method_score - attended_score + prev_score
        else:
            method_score = 0
            # 참석으로 변경 시 ( 참석 - 불참점수 ), 불참으로 변경 시 (불참점수 - 참석점수)
            attended_score_diff = attended.get(f"{grade}") - non_attended.get(f"{grade}")
            proceed_attended = attended_score_diff if is_attended == 1 else -attended_score_diff
            return method_score + proceed_attended + prev_score

    async def modify_user_score(
        self, 
        user_id:str, 
        prev_score : int, 
        new_score:int, 
        invitation_type:str
    ):
        # TODO 추후 ORM 이용해서 로직 수정할 것 
        try:
            
            if prev_score != 0:
                self.db.execute(
                    update(models.Score)
                    .where(models.Score.user_id == user_id)
                    .values(score=new_score)
                )
                
            else :
                self.db.execute(
                    insert(models.Score)
                    .values(
                        user_id=user_id, 
                        invitation_id=1 if invitation_type == "Wedding" else 0,
                        score=new_score,    
                    )
                )

            self.db.commit()
        except OperationalError as e:
            error_msg = "Failed to modify user score."
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_msg)

