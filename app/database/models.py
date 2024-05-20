from sqlalchemy import Column, Integer, String, func, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from app.database.settings import Base

import uuid

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    user_id = Column(String, nullable=False, primary_key=True, default=generate_uuid)
    email = Column(String, nullable=False)
    user_password = Column(String, nullable=False)
    user_name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    user_status = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.utc_timestamp())
    updated_at = Column(
        DateTime,
        nullable=False,
        default=func.utc_timestamp(),
        onupdate=func.utc_timestamp(),
    )