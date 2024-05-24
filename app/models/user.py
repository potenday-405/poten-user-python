from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum
from typing import Generic, TypeVar
DataT = TypeVar("DataT")

class UserCommonResponse(BaseModel, Generic[DataT]):
    message : str
    data : DataT

class UserSignup(BaseModel):
    user_name : str
    email :str
    user_password : str
    phone : str

class UserLogin(BaseModel):
    email :str
    user_password : str

class UserToken(BaseModel):
    access_token: str
    token_type:str

#TODO 이게 클래스로 굳이 정해야 하는지..? 다시 고민해보고 뺄지 말지 체크
class UserPassword(BaseModel):
    org_password : str = Field(description="기존 비밀번호")
    new_password:str = Field(description="새로운 비밀번호")

class UserProfile(BaseModel):
    user_id: str 
    email: str 
    user_password: str 
    user_status: str 
    user_name: str 
    phone: str 
    created_at : datetime
    updated_at : datetime


class MethodClass(Enum):
    DELETE = "DELETE"
    POST = "POST"

# Score점수 합산
class CalcUserScore(BaseModel):
    method: str
    is_attended : int
    