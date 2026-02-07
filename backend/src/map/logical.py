# map/logical.py
# 逻辑地图 数据结构
# 逻辑地图：提供给LLM进行路径节点选择
#
# 包含如下信息
# 节点 LogicalNode
# - id: 节点id
# - name: 节点名称
# - type: 节点类型
# - description: 节点描述信息
# 边 LogicalEdge
# - u: 起始节点id
# - v: 终止节点id
# - name: 边名称
# - cost: 边的费用
#

from pydantic import BaseModel, Field


class LogicalNode(BaseModel):
    id: str = Field(..., description="节点ID")
    name: str = Field(..., description="节点名称")
    type: str = Field(..., description="节点类型")
    description: str = Field("", description="节点描述信息", max_length=100)

    
    def __str__(self) -> str:
        return f"LogicalNode(id={self.id}, name={self.name}, type={self.type}, description={self.description})"


class LogicalEdge(BaseModel):
    u: str = Field(..., description="起始节点ID")
    v: str = Field(..., description="终止节点ID")
    # name: str = Field("", description="边名称", max_length=50)
    cost: int | None = Field(None, description="边的费用")


    def __str__(self) -> str:
        return f"LogicalEdge(u={self.u}, v={self.v}, cost={self.cost})"


class LogicalMap(BaseModel):
    nodes: list[LogicalNode] = Field(..., description="逻辑地图中的节点列表")
    edges: list[LogicalEdge] = Field(..., description="逻辑地图中的边列表")

    def __str__(self) -> str:
        return (
            f"LogicalMap(\n"
            f"  nodes=[\n"
            f"    " + ",\n    ".join(str(node) for node in self.nodes) + "\n"
            f"  ],\n"
            f"  edges=[\n"
            f"    " + ",\n    ".join(str(edge) for edge in self.edges) + "\n"
            f"  ]\n"
            f")"
        )


__all__ = [
    "LogicalNode",
    "LogicalEdge",
    "LogicalMap",
]