# 라우팅

from fastapi import APIRouter, Request,Header
from app.models.user import UserRequest
import httpx

router = APIRouter()

@router.get("")
async def get_users():
    return {
        "message" : "조회 테스트"
    }

@router.get("/{user_id}")
async def get_user(user_id:str):
    return {
        "user_id" : user_id
    }


@router.post("")
async def post_test(request:UserRequest, version: str = Header()):
    return {
        "data" : "일단 post"
    }