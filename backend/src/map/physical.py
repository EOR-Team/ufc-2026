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
# - u_node_id: 起始节点id
# - v_node_id: 终止节点id
# - name: 边名称
# - cost: 边的费用
#

from pydantic import BaseModel, Field


class PhysicalNode(BaseModel):
    id: str = Field(..., description="节点ID")
    name: str = Field(..., description="节点名称")
    x: int = Field(..., description="节点的x坐标")
    y: int = Field(..., description="节点的y坐标")


class PhysicalEdge(BaseModel):
    u_node_id: str = Field(..., description="起始节点ID")
    v_node_id: str = Field(..., description="终止节点ID")
    name: str = Field("", description="边名称", max_length=50)
    cost: int = Field(..., description="边的费用")


class PhysicalMap(BaseModel):
    nodes: list[PhysicalNode] = Field(..., description="物理地图中的节点列表")
    edges: list[PhysicalEdge] = Field(..., description="物理地图中的边列表")


__all__ = [
    "PhysicalNode",
    "PhysicalEdge",
    "PhysicalMap",
]
