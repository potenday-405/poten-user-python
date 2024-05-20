from pydantic import BaseModel
from typing import Optional

class UserSignup(BaseModel):
    user_name : str
    email :str
    user_password : str
    phone : str

class UserSignupResponse(BaseModel):
    message : str 
    
class UserInDB(BaseModel):
    hashed_password: str

class UserToken(BaseModel):
    access_token: str
    token_type:str

class User(BaseModel):
    username:str
    email:str | None = None