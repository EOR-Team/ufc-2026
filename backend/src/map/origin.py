# map/origin.py
# 数据结构 原地图信息
# 原地图：包含最原始的地图节点和边信息
#
# 包含如下信息
# 节点 Node
# - id: 节点id
# - x: 节点x坐标
# - y: 节点y坐标
# - type: 节点类型，主节点(main)或导航节点(nav)
# - description: 节点描述信息
# - name: 节点名称
# 边 Edge
# - u: 起始节点id
# - v: 终止节点id
# - name: 边名称
# - cost: 边的费用
#

from pydantic import BaseModel, Field
from typing import Literal


class OriginNode(BaseModel):
    """
    节点类，表示地图中的一个点
    """

    id: str = Field(..., description="节点id")
    x: int = Field(..., description="节点的x坐标")
    y: int = Field(..., description="节点的y坐标")
    type: Literal["main", "nav"] = Field(..., description="节点类型，主节点或导航节点")
    description: str = Field("", description="节点描述信息", max_length=100)
    name: str = Field("", description="节点名称", max_length=50)
    

    def __str__(self) -> str:
        return (
            f"OriginNode(id={self.id}, x={self.x}, y={self.y}, "
            f"type={self.type}, description={self.description}, name={self.name})"
        )


class OriginEdge(BaseModel):
    """
    边类，表示节点之间的连接
    """

    u: str = Field(..., description="起始节点id")
    v: str = Field(..., description="终止节点id")
    name: str = Field("", description="边名称", max_length=50)
    cost: int | None = Field(None, description="边的费用") # 需要进行计算


    def __str__(self) -> str:
        return f"OriginEdge(u={self.u}, v={self.v}, name={self.name}, cost={self.cost})"


class OriginMap(BaseModel):
    """
    原地图类，包含节点和边的信息
    """

    nodes: list[OriginNode] = Field(..., description="地图中的节点列表")
    edges: list[OriginEdge] = Field(..., description="地图中的边列表")


    def __str__(self) -> str:
        return (
            f"OriginMap(\n"
            f"  nodes=[\n"
            f"    " + ",\n    ".join(str(node) for node in self.nodes) + "\n"
            f"  ],\n"
            f"  edges=[\n"
            f"    " + ",\n    ".join(str(edge) for edge in self.edges) + "\n"
            f"  ]\n"
            f")"
        )

    
__all__ = [
    "OriginNode",
    "OriginEdge",
    "OriginMap",
]
