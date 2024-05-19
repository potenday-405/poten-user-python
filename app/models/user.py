from pydantic import BaseModel
from typing import Optional

class UserRequest(BaseModel):
    name : str
    email :str
    password : str
    phone : Optional[str] = None
    
