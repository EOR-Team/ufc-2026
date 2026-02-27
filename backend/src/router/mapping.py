"""
router/mapping.py
地图功能 路由
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from src.map.tools import map


map_router = APIRouter(prefix="/map")


@map_router.get("/")
async def get_map():
    """
    获取地图数据
    """

    return JSONResponse( content=map, status_code=200, media_type="application/json" )
