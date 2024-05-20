from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from app.core.config import TEST_DB_USER ,TEST_DB_PASSWORD ,TEST_DB_HOST ,TEST_DB_PORT ,TEST_DB_BASE

DB_URL = f"mysql+pymysql://{TEST_DB_USER}:{TEST_DB_PASSWORD}@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_BASE}"

class Engineconn:
    def __init__(self):
        self.engine = create_engine(DB_URL, pool_recycle=500)

    @staticmethod
    def create_session():
        Session = sessionmaker(bind=Engineconn().engine)
        session = Session()
        return session

    @staticmethod
    def create_connection():
        conn = Engineconn().engine.connect()
        return conn