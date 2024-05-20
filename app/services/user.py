from sqlalchemy.orm import Session
from app.database import models
from app.models.user import UserSignup
from sqlalchemy import insert
# from sqlalchemy import and_, delete, func, insert, select, text, update

class UserService():
    def __init__(self, db:Session):
        self.db = db

    async def check_existed_user(self, email:str):
        """회원가입 시 email을 통해 이미 가잆된 사용자가 있는지 반환

        :return : 유저 정보
        """
        User = models.User
        user = self.db.query(User).filter(User.email == email).all()
        return user

    async def create_user(self, user:UserSignup):
        """회원가입"""
        self.db.execute(
            insert(models.User).values(
            **user.dict(),
            user_status='act'
        ))

        self.db.commit()
        
        return user

    async def get_users(self):
        return self.db.query(models.User).all()