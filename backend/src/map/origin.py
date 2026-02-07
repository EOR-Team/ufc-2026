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
# - u_node_id: 起始节点id
# - v_node_id: 终止节点id
# - name: 边名称
#

from pydantic import BaseModel, Field
from typing import Literal


class OriginNode(BaseModel):
    """
    节点类，表示地图中的一个点
    """

    # id: str = Field(..., description="节点id")
    # x: int = Field(..., description="节点的x坐标")
    # y: int = Field(..., description="节点的y坐标")
    type: Literal["main", "nav"] = Field(..., description="节点类型，主节点或导航节点")
    description: str = Field("", description="节点描述信息", max_length=100)
    name: str = Field("", description="节点名称", max_length=50)


class OriginEdge(BaseModel):
    """
    边类，表示节点之间的连接
    """

    # u_node_id: str = Field(..., description="起始节点id")
    # v_node_id: str = Field(..., description="终止节点id")
    # name: str = Field("", description="边名称", max_length=50)
    pass


class OriginMap(BaseModel):
    """
    原地图类，包含节点和边的信息
    """

    nodes: list[OriginNode] = Field(..., description="地图中的节点列表")
    edges: list[OriginEdge] = Field(..., description="地图中的边列表")

    
__all__ = [
    "OriginNode",
    "OriginEdge",
    "OriginMap",
]
