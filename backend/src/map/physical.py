# map/physical.py
# 物理地图 数据结构
# 物理地图：用于 Dijkstra 算法计算最短路径
#
# 包含如下信息
# 节点 PhysicalNode
# - id: 节点id
# - name: 节点名称
# - type: 节点类型
# - description: 节点描述信息
# 边 PhysicalEdge
# - u_node_id: 起始节点id
# - v_node_id: 终止节点id
# - name: 边名称
# - manhattan_distance: 边的距离 (曼哈顿距离)
#

from pydantic import BaseModel, Field


class PhysicalNode(BaseModel):
    id: int = Field(..., description="节点ID")
    name: str = Field(..., description="节点名称")
    type: str = Field(..., description="节点类型")
    description: str = Field("", description="节点描述信息", max_length=100)


class PhysicalEdge(BaseModel):
    u_node_id: int = Field(..., description="起始节点ID")
    v_node_id: int = Field(..., description="终止节点ID")
    name: str = Field("", description="边名称", max_length=50)
    manhattan_distance: int = Field(..., description="边的曼哈顿距离")


class PhysicalMap(BaseModel):
    nodes: list[PhysicalNode] = Field(..., description="物理地图中的节点列表")
    edges: list[PhysicalEdge] = Field(..., description="物理地图中的边列表")


__all__ = [
    "PhysicalNode",
    "PhysicalEdge",
    "PhysicalMap",
]
