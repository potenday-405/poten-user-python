from fastapi import FastAPI
from app.api.user.main import router as v1_router

app = FastAPI(title="회원관련 API입니다.")

app.include_router(v1_router, prefix="/user", tags=["user"])