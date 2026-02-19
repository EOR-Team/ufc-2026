# smart_triager/triager/typedef.py
# 类型定义
#

from pydantic import BaseModel, Field, ValidationError


class ConditionCollectorOutput(BaseModel):
    """
    对当前患者明确症状的总结
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
