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
# - u_node_id: 起始节点id
# - v_node_id: 终止节点id
# - name: 边名称
# - cost: 边的费用
#

from pydantic import BaseModel, Field


class LogicalNode(BaseModel):
    id: str = Field(..., description="节点ID")
    name: str = Field(..., description="节点名称")
    type: str = Field(..., description="节点类型")
    description: str = Field("", description="节点描述信息", max_length=100)


class LogicalEdge(BaseModel):
    u_node_id: str = Field(..., description="起始节点ID")
    v_node_id: str = Field(..., description="终止节点ID")
    name: str = Field("", description="边名称", max_length=50)
    cost: int = Field(..., description="边的费用")


class LogicalMap(BaseModel):
    nodes: list[LogicalNode] = Field(..., description="逻辑地图中的节点列表")
    edges: list[LogicalEdge] = Field(..., description="逻辑地图中的边列表")


__all__ = [
    "LogicalNode",
    "LogicalEdge",
    "LogicalMap",
]