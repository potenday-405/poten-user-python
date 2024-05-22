from sqlalchemy.orm import Session
from app.database import models
from app.models.user import UserSignup, UserProfile, UserPassword, CalcUserScore
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

    async def get_score(self, user_id:str):
        score_info = self.db.query(models.Score).filter(models.Score.user_id == user_id).first()
        return score_info.score



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

        method, is_attendeed = body.method, body.is_attendeed

        attended_score = attended.get(f"{grade}") if is_attendeed == 1 else int(non_attended.get(f"{grade}"))

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
            proceed_attended = attended_score_diff if is_attendeed == 1 else -attended_score_diff
            return method_score + proceed_attended + prev_score

    async def modify_user_score(self, user_id:str, new_score:int):
        self.db.execute(
            update(models.Score)
            .where(models.Score.user_id == user_id)
            .values(score=new_score)
        )

        self.db.commit()

