"""
router/triager.py
智能分诊功能 路由
"""

from pydantic import BaseModel, Field
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from src.smart_triager.typedef import *
from src.smart_triager.triager.workflow import (
    collect_conditions as collect_conditions_workflow,
    select_clinic as select_clinic_workflow,
    collect_requirement as collect_requirement_workflow,
    patch_route as patch_route_workflow,
    modify_route as modify_route_workflow,
)
from src.map.tools import map
from src.smart_triager.car.parser import parse_route_to_commands


triager_router = APIRouter(prefix="/triager")


class GetRoutePatchRequest(BaseModel):
    """
    获取路线修改方案的请求体
    """

    user_input: str = Field(..., description="用户输入的需求描述")

    origin_route: list[LocationLink] = Field(..., description="原路线列表")

    online_model: bool = Field(default=True, description="是否使用在线模型进行需求提取和路线修改")


class CollectConditionsRequest(BaseModel):
    """
    收集症状信息的请求体
    """

    user_input: str = Field(..., description="用户输入的病症描述")
    online_model: bool = Field(default=True, description="是否使用在线模型进行症状提取")


class SelectClinicRequest(BaseModel):
    """
    选择诊室的请求体
    """

    conditions: ConditionCollectorOutput = Field(..., description="结构化症状信息")
    online_model: bool = Field(default=True, description="是否使用在线模型进行诊室选择")


class CollectRequirementRequest(BaseModel):
    """
    收集需求的请求体
    """

    user_input: str = Field(..., description="用户输入的需求描述")
    online_model: bool = Field(default=True, description="是否使用在线模型进行需求提取")


class PatchRouteRequest(BaseModel):
    """
    修改路线的请求体
    """

    destination_clinic_id: str = Field(..., description="目的地诊室ID")
    requirement_summary: list[Requirement] = Field(..., description="用户需求摘要列表")
    origin_route: list[LocationLink] = Field(..., description="原路线列表")
    online_model: bool = Field(default=True, description="是否使用在线模型进行路线修改")


class ParseCommandsRequest(BaseModel):
    """
    解析路线为小车移动指令的请求体
    """
    origin_route: list[LocationLink] = Field(..., description="原始路线列表")
    # 注意：与现有API保持一致，可能添加online_model参数，但当前不需要


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
    rsp = await modify_route_workflow(user_input, origin_route, online_model)

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


@triager_router.post("/collect_conditions/")
async def collect_conditions(
    request: CollectConditionsRequest
):
    """
    从用户输入中提取结构化症状信息
    """

    user_input = request.user_input
    online_model = request.online_model

    rsp = await collect_conditions_workflow(user_input, online_model)

    if rsp:
        return JSONResponse(
            content={ "success": True, "data": rsp.model_dump() },
            status_code=200,
            media_type="application/json"
        )
    else:
        return JSONResponse(
            content={ "success": False, "error": "Failed to collect conditions." },
            status_code=500,
            media_type="application/json"
        )


@triager_router.post("/select_clinic/")
async def select_clinic(
    request: SelectClinicRequest
):
    """
    根据结构化症状信息选择诊室
    """

    conditions = request.conditions
    online_model = request.online_model

    rsp = await select_clinic_workflow(conditions, online_model)

    if rsp:
        return JSONResponse(
            content={ "success": True, "data": { "clinic_selection": rsp } },
            status_code=200,
            media_type="application/json"
        )
    else:
        return JSONResponse(
            content={ "success": False, "error": "Failed to select clinic." },
            status_code=500,
            media_type="application/json"
        )


@triager_router.post("/collect_requirement/")
async def collect_requirement(
    request: CollectRequirementRequest
):
    """
    从用户输入中提取个性化需求
    """

    user_input = request.user_input
    online_model = request.online_model

    rsp = await collect_requirement_workflow(user_input, online_model)

    if rsp:
        return JSONResponse(
            content={ "success": True, "data": [req.model_dump() for req in rsp] },
            status_code=200,
            media_type="application/json"
        )
    else:
        return JSONResponse(
            content={ "success": False, "error": "Failed to collect requirements." },
            status_code=500,
            media_type="application/json"
        )


@triager_router.post("/patch_route/")
async def patch_route(
    request: PatchRouteRequest
):
    """
    根据目的地诊室和需求摘要修改原路线
    """

    destination_clinic_id = request.destination_clinic_id
    requirement_summary = request.requirement_summary
    origin_route = request.origin_route
    online_model = request.online_model

    rsp = await patch_route_workflow(destination_clinic_id, requirement_summary, origin_route, online_model)

    if rsp:
        return JSONResponse(
            content={ "success": True, "data": rsp.model_dump() },
            status_code=200,
            media_type="application/json"
        )
    else:
        return JSONResponse(
            content={ "success": False, "error": "Failed to patch route." },
            status_code=500,
            media_type="application/json"
        )


@triager_router.post("/parse_commands/")
async def parse_commands(
    request: ParseCommandsRequest
):
    """
    将路线转换为小车移动指令
    """
    origin_route = request.origin_route

    try:
        # 调用路径解析器
        commands = parse_route_to_commands(origin_route, map)

        return JSONResponse(
            content={"success": True, "data": commands.model_dump()},
            status_code=200,
            media_type="application/json"
        )
    except ValueError as e:
        # 路径不存在或输入无效
        return JSONResponse(
            content={"success": False, "error": str(e)},
            status_code=500,
            media_type="application/json"
        )
    except Exception as e:
        # 其他未知错误
        return JSONResponse(
            content={"success": False, "error": f"Internal error: {str(e)}"},
            status_code=500,
            media_type="application/json"
        )

