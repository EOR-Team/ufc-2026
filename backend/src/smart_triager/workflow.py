"""
smart_triager/workflow.py
工作流
"""

import asyncio

from src import logger
from src.smart_triager.typedef import *
from src.smart_triager.triager import *


_CC_MAX_RETRY = 3

async def collect_conditions(
    user_input: str,
    online_model: bool
) -> str | None:
    """
    从用户的输入中 提取出与身体状况相关的信息
    并根据现有地图结构 给出分诊的诊室建议

    Args:
        user_input (str): 用户的原始输入
        online_model (bool): 是否使用在线的模型进行推理
    Returns:
        str: 建议的分诊诊室的ID
        None: 超过 `_CC_MAX_RETRY` 的尝试次数后也无法解析 返回空
    """

    _retry_time = 0

    while _retry_time < _CC_MAX_RETRY:

        if online_model:
            # 使用在线模型推理
            rsp = await collect_conditions_online(user_input)
        else:
            # 使用离线模型推理
            rsp = await collect_conditions_offline(user_input)
        
        if rsp:
            # 能够**正常**获取返回值 直接退出返回
            return rsp.clinic_selection
        
        # 返回为空 重新解析
        _retry_time += 1
        logger.warning(f"Collect conditions failed. Already retry {_retry_time} times. Retrying...")
    
    # 最终还是没有解析成功 返回空
    return None


_CR_MAX_RETRY = 3

async def collect_requirement(
    user_input: str,
    online_model: bool
) -> list[Requirement] | None:
    """
    从用户的输入中提取出他的个性化需求

    Args:
        user_input (str): 用户的原始输入
        online_model (bool): 是否使用在线模型进行推理
    Returns:
        list[Requirement]: 需求清单
        None: 重试 `_CR_MAX_RETRY` 次后 仍然解析失败 返回空
    """

    _retry_time = 0

    while _retry_time < _CR_MAX_RETRY:

        if online_model:
            # 使用在线模型推理
            rsp = await collect_requirement_online(user_input)
        else:
            # 使用离线模型推理
            rsp = await collect_requirement_offline(user_input)
        
        if rsp:
            # 能够**正常**获取返回值 直接退出返回
            return rsp.requirements
        
        # 返回为空 重新解析
        _retry_time += 1
        logger.warning(f"Collect requirement failed. Already retry {_retry_time} times. Retrying...")
    
    # 最终还是没有解析成功 返回空
    return None
            
    
_PR_MAX_RETRY = 3

async def patch_route(
    destination_clinic_id: str,
    requirement_summary: list[Requirement],
    origin_route: list[LocationLink],
    online_model: bool
) -> RoutePatcherOutput | None:
    """
    根据用户的目的地诊室ID和需求摘要 对原路线进行修改
    以满足用户的个性化需求

    Args:
        destination_clinic_id (str): 用户的目的地诊室ID
        requirement_summary (list[Requirement]): 用户的需求摘要列表
        origin_route (list[LocationLink]): 原路线列表，默认为基于surgery_clinic生成的路线
        online_model (bool): 是否使用在线模型进行推理

    Returns:
        RoutePatcherOutput: 路线修改方案输出对象
        None: 重试 `_CR_MAX_RETRY` 次后 仍然解析失败 返回空
    """

    _retry_time = 0

    while _retry_time < _PR_MAX_RETRY:

        if online_model:
            # 使用在线模型推理
            rsp = await patch_route_online(destination_clinic_id, requirement_summary, origin_route)
        else:
            # 使用离线模型推理
            rsp = await patch_route_offline(destination_clinic_id, requirement_summary, origin_route)
        
        if rsp:
            # 能够**正常**获取返回值 直接退出返回
            return rsp
        
        # 返回为空 重新解析
        logger.warning(f"Patch route failed. Already retry {_retry_time} times. Retrying...")
        _retry_time += 1
    
    # 最终还是没有解析成功 返回空
    return None


async def modify_route(
    user_input: str,
    origin_route: list[LocationLink],
    online_model: bool
) -> RoutePatcherOutput | None:
    """
    从用户的输入中提取出他的个性化需求
    并根据现有地图结构 给出分诊的诊室建议
    最后根据目的地诊室ID和需求摘要 对原路线进行修改
    以满足用户的个性化需求

    Args:
        user_input (str): 用户的原始输入
        origin_route (list[LocationLink]): 原路线列表
        online_model (bool): 是否使用在线模型进行推理
    Returns:
        RoutePatcherOutput: 路线修改方案输出对象
        None: 解析失败 返回空
    """

    # 如果使用在线模型推理 那么允许异步并行执行
    # 如果使用离线模型推理 `llama-cpp-python` 针对同一个模型实例只能串行执行
    # 但是在这个场景下 使用了两个不同的离线模型实例 不会相互干扰 所以也可以异步并行执行

    if online_model:
        cc_output, cr_output = await asyncio.gather(
            collect_conditions_online(user_input),
            collect_requirement_online(user_input)
        )
    else:
        cc_output, cr_output = await asyncio.gather(
            collect_conditions_offline(user_input),
            collect_requirement_offline(user_input)
        )
    
    # 获取到数据之后 修改路线
    if not cc_output or not cr_output:
        # 上述任一解析失败 直接返回空 无法修改路线
        return None

    return await patch_route(
        cc_output.clinic_selection,
        cr_output.requirements,
        origin_route,
        online_model
    )

    
__all__ = [
    "modify_route",
]
