# 디비 커넥션

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.core.config import (
    TEST_DB_USER,
    TEST_DB_PASSWORD,
    TEST_DB_HOST,
    TEST_DB_PORT,
    TEST_DB_BASE
)

TEST_DB_URL = f"mysql+pymysql://{TEST_DB_USER}:{TEST_DB_PASSWORD}@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_BASE}"

engine = create_engine(TEST_DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()