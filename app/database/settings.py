# 디비 커넥션

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,scoped_session
from sqlalchemy.ext.declarative import declarative_base
from app.core.config import (
    TEST_DB_USER,
    TEST_DB_PASSWORD,
    TEST_DB_HOST,
    TEST_DB_PORT,
    TEST_DB_BASE
)

TEST_DB_URL = f"mysql+pymysql://{TEST_DB_USER}:{TEST_DB_PASSWORD}@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_BASE}"

# 최대 연결시간 1시간, 연결 요청 대기 30초로 지정 
engine = create_engine( TEST_DB_URL, pool_recycle=3600, pool_timeout=30)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = scoped_session(SessionLocal)

Base = declarative_base()

def get_test_db():
    db = db_session()
    try:
        yield db
    finally:
        db.close()
