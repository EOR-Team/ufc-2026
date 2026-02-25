# smart_triager/car/typedef.py
# 小车控制模块类型定义

from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field


class Orientation(str, Enum):
    """
    小车转向方向枚举
    """
    straight = "straight"
    left = "left"
    right = "right"
    # 注意：180°掉头分解为两个90°转向，不单独定义u_turn


class CarAction(BaseModel):
    """
    小车单个动作：先转向，再移动指定距离
    """
    orientation: Orientation = Field(
        ...,
        description="转向方向（left/right/straight）"
    )
    distance: int = Field(
        ...,
        description="转向后的移动距离，应避免为0",
        ge=0  # 距离非负
    )


class CarCommandsOutput(BaseModel):
    """
    小车移动指令序列输出
    """
    actions: list[CarAction] = Field(
        ...,
        description="小车动作序列，按顺序执行"
    )