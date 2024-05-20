from fastapi import FastAPI
from app.routes.user import router

app = FastAPI(title="회원관련 API입니다.")

app.include_router(router, prefix="/user", tags=["user"])