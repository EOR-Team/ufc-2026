# map/loader.py
# 地图加载器
#

from pydantic import BaseModel, Field
from typing import Literal


class Node(BaseModel):
    """
    地图节点
    """

    id: str = Field(..., description="节点唯一标识符")

    x: float = Field(..., description="节点的X坐标")

    y: float = Field(..., description="节点的Y坐标")

    type: Literal["main", "nav"] = Field(..., description="节点类型，主节点或导航节点")

    name: str | None = Field(None, description="节点名称", max_length=50)

    description: str | None = Field(None, description="节点描述", max_length=200)


    def __str__(self) -> str:
        return f"Node(id={self.id}, x={self.x}, y={self.y}, type={self.type}, name={self.name}, description={self.description})"
    

class Edge(BaseModel):
    """
    地图边
    """

    u_node: str = Field(..., description="边的起始节点ID", alias="u")

    v_node: str = Field(..., description="边的终止节点ID", alias="v")

    cost: int | None = Field(None, description="边的费用")

    name: str | None = Field(None, description="边名称", max_length=50)


    def __str__(self) -> str:
        return f"Edge(u_node={self.u_node}, v_node={self.v_node}, name={self.name}, cost={self.cost})"


class Map(BaseModel):
    """
    地图
    """

    nodes: list[Node] = Field(..., description="地图中的节点列表")

    edges: list[Edge] = Field(..., description="地图中的边列表")


class TreeNode(Node):
    """
    地图树 节点
    """

    children: list["TreeNode"] = Field(default_factory=list, description="子节点列表")


__all__ = [
    "Node",
    "Edge",
    "Map",
    "TreeNode",
]
