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
) -> ConditionCollectorOutput | None:
    """
    从用户的输入中提取结构化症状信息

    Args:
        user_input (str): 用户的原始输入
        online_model (bool): 是否使用在线的模型进行推理
    Returns:
        ConditionCollectorOutput: 结构化症状信息
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
            return rsp
        
        # 返回为空 重新解析
        _retry_time += 1
        logger.warning(f"Collect conditions failed. Already retry {_retry_time} times. Retrying...")
    
    # 最终还是没有解析成功 返回空
    return None


async def select_clinic(
    conditions: ConditionCollectorOutput,
    online_model: bool
) -> str | None:
    """
    根据结构化症状信息选择诊室

    Args:
        conditions (ConditionCollectorOutput): 结构化症状信息
        online_model (bool): 是否使用在线的模型进行推理
    Returns:
        str: 选择的诊室ID
        None: 超过 `_SC_MAX_RETRY` 的尝试次数后也无法解析 返回空
    """

    _retry_time = 0
    _SC_MAX_RETRY = 3

    while _retry_time < _SC_MAX_RETRY:

        if online_model:
            # 使用在线模型推理
            rsp = await select_clinic_online(conditions)
        else:
            # 使用离线模型推理
            rsp = await select_clinic_offline(
                body_parts=conditions.body_parts,
                duration=conditions.duration,
                severity=conditions.severity,
                description=conditions.description,
                other_relevant_information=conditions.other_relevant_information
            )
        
        if rsp:
            # 能够**正常**获取返回值 直接退出返回
            return rsp.clinic_selection
        
        # 返回为空 重新解析
        _retry_time += 1
        logger.warning(f"Select clinic failed. Already retry {_retry_time} times. Retrying...")
    
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
    完整的工作流：收集症状、选择诊室、收集需求、修改路线

    Args:
        user_input: 用户输入的病症描述
        origin_route: 原路线列表
        online_model: 是否使用在线模型

    Returns:
        RoutePatcherOutput: 路线修改方案
        None: 任何一步失败时返回None
    """

    # 1. 收集症状信息
    conditions = await collect_conditions(user_input, online_model)
    if not conditions:
        logger.warning("Failed to collect conditions in modify_route")
        return None

    # 2. 选择诊室
    clinic_id = await select_clinic(conditions, online_model)
    if not clinic_id:
        logger.warning("Failed to select clinic in modify_route")
        return None

    # 3. 收集需求
    requirements = await collect_requirement(user_input, online_model)
    if not requirements:
        logger.warning("Failed to collect requirements in modify_route")
        return None

    # 4. 修改路线
    patched_route = await patch_route(clinic_id, requirements, origin_route, online_model)
    if not patched_route:
        logger.warning("Failed to patch route in modify_route")
        return None

    return patched_route


__all__ = [
    "collect_conditions",
    "collect_requirement",
    "select_clinic",
    "patch_route",
    "modify_route"
]
