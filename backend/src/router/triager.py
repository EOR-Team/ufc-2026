"""
router/triager.py
智能分诊功能 路由
"""

from pydantic import BaseModel, Field
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from src.smart_triager.typedef import *
from src.smart_triager.workflow import *


triager_router = APIRouter(prefix="/triager")


class GetRoutePatchRequest(BaseModel):
    """
    获取路线修改方案的请求体
    """

    user_input: str = Field(..., description="用户输入的需求描述")

    origin_route: list[LocationLink] = Field(..., description="原路线列表")

    online_model: bool = Field(default=True, description="是否使用在线模型进行需求提取和路线修改")


@triager_router.post("/get_route_patch/")
async def get_route_patch(
    request: GetRoutePatchRequest
):
    """
    根据用户输入的需求，生成对原路线的修改方案
    """

    # 从请求体中获取参数
    user_input = request.user_input
    origin_route = request.origin_route
    online_model = request.online_model

    # 调用工作流函数 获取路线修改方案
    rsp = await modify_route(user_input, origin_route, online_model)

    if rsp:
        # 能够**正常**获取返回值 直接退出返回
        return JSONResponse(
            content={ "success": True, "data": rsp.model_dump_json() }, 
            status_code=200,
            media_type="application/json"
        )
    else:
        # 解析失败 返回错误信息
        return JSONResponse(
            content={ "success": False, "error": "Failed." }, 
            status_code=500,
            media_type="application/json"
        )

origin_route_list = [
    {
        "this": "entrance",
        "next": "registration_center"
    },
    {
        "this": "registration_center",
        "next": "surgery_clinic"
    },
    {
        "this": "surgery_clinic",
        "next": "pharmacy"
    },
    {
        "this": "pharmacy",
        "next": "exit"
    }
]

