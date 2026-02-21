from fastapi import APIRouter
from src.router.triager import triager_router

api_router = APIRouter(prefix="/api")
api_router.include_router(triager_router)
