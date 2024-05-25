from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.user import router

app = FastAPI(title="회원관련 API입니다.")

origins = [
    "http://localhost",
    "http://localhost:3000",
    "https://poten-fe.vercel.app",
    "https://tikitakaapi.site",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/user", tags=["user"])