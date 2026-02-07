# map/physical.py
# 物理地图 数据结构
# 物理地图：用于 Dijkstra 算法计算最短路径
#
# 包含如下信息
# 节点 PhysicalNode
# - id: 节点id
# - name: 节点名称
# - x: 节点x坐标
# - y: 节点y坐标
# 边 PhysicalEdge
# - u: 起始节点id
# - v: 终止节点id
# - name: 边名称
# - cost: 边的费用
#

from pydantic import BaseModel, Field


class PhysicalNode(BaseModel):
    id: str = Field(..., description="节点ID")
    name: str = Field(..., description="节点名称")
    x: int = Field(..., description="节点的x坐标")
    y: int = Field(..., description="节点的y坐标")


    def __str__(self) -> str:
        return f"PhysicalNode(id={self.id}, name={self.name}, x={self.x}, y={self.y})"


class PhysicalEdge(BaseModel):
    u: str = Field(..., description="起始节点ID")
    v: str = Field(..., description="终止节点ID")
    name: str = Field("", description="边名称", max_length=50)
    cost: int | None = Field(None, description="边的费用")


    def __str__(self) -> str:
        return f"PhysicalEdge(u={self.u}, v={self.v}, name={self.name}, cost={self.cost})"


class PhysicalMap(BaseModel):
    nodes: list[PhysicalNode] = Field(..., description="物理地图中的节点列表")
    edges: list[PhysicalEdge] = Field(..., description="物理地图中的边列表")


    def __str__(self) -> str:
        return (
            f"PhysicalMap(\n"
            f"  nodes=[\n"
            f"    " + ",\n    ".join(str(node) for node in self.nodes) + "\n"
            f"  ],\n"
            f"  edges=[\n"
            f"    " + ",\n    ".join(str(edge) for edge in self.edges) + "\n"
            f"  ]\n"
            f")"
        )


__all__ = [
    "PhysicalNode",
    "PhysicalEdge",
    "PhysicalMap",
]
