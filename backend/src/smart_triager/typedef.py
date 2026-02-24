# smart_triager/triager/typedef.py
# 类型定义
#

from typing import Literal
from pydantic import BaseModel, Field, ValidationError


class ConditionCollectorOutput(BaseModel):
    """
    对当前患者明确症状的总结（不含诊室选择）
    """

    body_parts: str = Field(..., description="感到不适的身体部位")

    duration: str = Field(..., description="症状持续的时间")

    severity: str = Field(..., description="症状的严重程度")

    description: str = Field(..., description="症状的具体描述")

    other_relevant_information: list[str] = Field(default_factory=list, description="其他与诊断患者病情和进行分诊相关的信息")


class Requirement(BaseModel):
    """
    患者的具体需求
    """

    when: str = Field(..., description="执行某需求的**时机**，例如：在医生问诊过程中、在医生开具处方后、在拿药时等")

    what: str = Field(..., description="患者的具体需求内容，例如：需要医生在问诊过程中多问一些关于症状的问题、需要医生开具某种药物、需要药房提供送药上门服务等")


class RequirementCollectorOutput(BaseModel):
    """
    需求收集器的输出
    """

    requirements: list[Requirement] = Field(..., description="患者的具体需求列表")


class LocationLink(BaseModel):
    """
    最终路径中地点之间的链接 单向
    """

    this: str = Field(..., description="当前地点的ID")

    next: str = Field(..., description="下一个地点的ID")


class LocationLinkPatch(BaseModel):
    """
    对链接做出的修改 结构化

    **注意**：
    在死的逻辑中会默认先加载 `delete` 类型的patch，再加载 `insert` 类型的patch。
    这样设计有便于模型理解和输出，模型只需要根据原路线进行修改，而不需要考虑修改的先后顺序。
    """

    type: Literal["insert", "delete"] = Field(..., description="修改的类型: insert/delete")

    previous: str = Field(..., description="上一个地点的ID")

    this: str = Field(..., description="当前地点的ID")

    next: str = Field(..., description="下一个地点的ID")


class RoutePatcherOutput(BaseModel):
    """
    路线修改器的输出
    """

    patches: list[LocationLinkPatch] = Field(..., description="对原路线的修改方案列表")


def generate_route_by_ids(*ids: str) -> list[LocationLink]:
    """
    按顺序生成 LocationLink 列表
    
    Args:
        *ids: str ID 列表
    Returns:
        list[LocationLink] LocationLink列表
    """

    return [
        LocationLink(this=ids[i], next=ids[i + 1]) for i in range(len(ids) - 1)
    ]


class ClinicSelectionOutput(BaseModel):
    """
    诊室选择结果
    """

    clinic_selection: str = Field(..., description="诊室ID")