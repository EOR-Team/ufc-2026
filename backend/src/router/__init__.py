from fastapi import APIRouter
from src.router.triager import triager_router
from src.router.voice import voice_router

api_router = APIRouter(prefix="/api")
api_router.include_router(triager_router)
api_router.include_router(voice_router)
