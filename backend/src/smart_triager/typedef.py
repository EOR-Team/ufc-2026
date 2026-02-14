# smart_triager/triager/typedef.py
# 类型定义
#

from pydantic import BaseModel, Field, ValidationError


class CurrentSummary(BaseModel):
    """
    对当前患者明确症状的总结
    """

    body_parts: str = Field(..., description="感到不适的身体部位")

    duration: str = Field(..., description="症状持续的时间")

    severity: str = Field(..., description="症状的严重程度")


class MissingField(BaseModel):
    """
    患者症状描述中不合标准的字段 的相关信息
    """

    name: str = Field(..., description="不合标准的字段的名称")

    reason: str = Field(..., description="该字段不合标准的原因 与 患者对其类似的描述")


class ConditionCollectorOutput(BaseModel):
    """
    信息收集器的输出
    """

    current_summary: CurrentSummary = Field(..., description="当前患者明确症状的总结")

    missing_fields: list[MissingField] = Field(..., description="患者症状描述中不合标准的字段 的相关信息列表")
