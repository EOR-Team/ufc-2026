# map/tools.py
# 地图相关工具函数
#

import json

from src.map.logical import *
from src.map.physical import *
from src.map.origin import *


def check_map_cost(map: OriginMap | PhysicalMap | LogicalMap) -> bool:
    """
    检查地图数据中 cost 是否有效
    若 存在 cost 为 None 或负值则视为无效

    Args:
        map (OriginMap | PhysicalMap | LogicalMap): 地图数据

    Returns:
        bool: 是否有效
    """

    for edge in map.edges:
        if edge.cost is None or edge.cost < 0:
            return False
    return True


def calculate_cost(a: tuple[int, int], b: tuple[int, int]) -> int:
    """
    计算两节点之间的费用（曼哈顿距离）
    """

    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def calculate_all_cost(map: OriginMap | PhysicalMap) -> None:
    """
    计算地图中所有边的费用

    Args:
        map (OriginMap | PhysicalMap): 地图
    """

    if isinstance(map, OriginMap):
        _map = PhysicalMap(
            nodes=[
                PhysicalNode(
                    id=node.id, 
                    name=node.name,
                    x=node.x,
                    y=node.y
                ) for node in map.nodes
            ], # 转换节点
            edges=[
                PhysicalEdge(
                    u=edge.u, 
                    v=edge.v, 
                    name=edge.name, 
                    cost=None
                ) for edge in map.edges
            ], # 转换边 *注意：费用先设为 None*
        )
    else:
        _map = map

    # 缓存节点坐标便于查找
    nodes_dict: dict[str, tuple[int, int]] = {}
    for node in _map.nodes:
        nodes_dict[node.id] = (node.x, node.y)
    
    # 计算每条边的费用
    for edge in _map.edges:
        u_node = nodes_dict[edge.u]
        v_node = nodes_dict[edge.v]
        edge.cost = calculate_cost(u_node, v_node)

    # **应用回原map**
    if isinstance(map, OriginMap):
        map.edges = [
            OriginEdge(
                u=_map.edges[i].u,
                v=_map.edges[i].v,
                name=_map.edges[i].name,
                cost=_map.edges[i].cost,
            ) for i in range(len(_map.edges))
        ]
    else:
        map.edges = _map.edges

def load_origin_map_from_json(source_json: str) -> OriginMap:
    """
    从 JSON 字符串加载原地图数据
    """

    source_obj = json.loads(source_json)
    origin_map = OriginMap(
        nodes=[
            OriginNode(
                id=node_obj["id"],
                name=node_obj.get("name", ""), # nav 节点名称可为空
                x=node_obj["x"],
                y=node_obj["y"],
                type=node_obj["type"],
                description=node_obj.get("description", ""),
            ) for node_obj in source_obj["nodes"]
        ],
        edges=[
            OriginEdge(
                u=edge_obj["u"],
                v=edge_obj["v"],
                name=edge_obj.get("name", ""),
                cost=None,
            ) for edge_obj in source_obj["edges"]
        ],
    ) # **注意：仍未计算边的费用**
    calculate_all_cost(origin_map) # 计算所有边的费用

    assert check_map_cost(origin_map), "地图边的费用计算错误" # 检查费用是否有效

    return origin_map


def convert_origin_to_physical_map(origin_map: OriginMap) -> PhysicalMap:
    """
    将原地图转换为物理地图
    """

    physical_map = PhysicalMap(
        nodes=[
            PhysicalNode(
                id=node.id,
                name=node.name,
                x=node.x,
                y=node.y,
            ) for node in origin_map.nodes
        ],
        edges=[
            PhysicalEdge(
                u=edge.u,
                v=edge.v,
                name=edge.name,
                cost=edge.cost,
            ) for edge in origin_map.edges
        ],
    )

    assert check_map_cost(physical_map), "物理地图边的费用计算错误" # 检查费用是否有效

    return physical_map


def convert_origin_to_logical_map(origin_map: OriginMap) -> LogicalMap:
    """
    将原地图转换为逻辑地图
    """

    logical_map = LogicalMap(
        nodes=[
            LogicalNode(
                id=node.id,
                name=node.name,
                type="main" if node.type == "main" else "nav",
                description=node.description,
            ) for node in origin_map.nodes
        ],
        edges=[
            LogicalEdge(
                u=edge.u,
                v=edge.v,
                name=edge.name,
                cost=edge.cost,
            ) for edge in origin_map.edges
        ],
    )

    assert check_map_cost(logical_map), "逻辑地图边的费用计算错误" # 检查费用是否有效

    return logical_map


def show_map_info(map: OriginMap | PhysicalMap | LogicalMap) -> None:
    """
    显示地图的基本信息
    """

    print(f"节点数量: {len(map.nodes)}")
    print(f"边数量: {len(map.edges)}")

    for node in map.nodes:
        print(f"节点 ID: {node.id}\n- 名称: {getattr(node, 'name', '')}\n- 坐标: ({getattr(node, 'x', 'N/A')}, {getattr(node, 'y', 'N/A')})\n- 类型: {getattr(node, 'type', 'N/A')}\n- 描述: {getattr(node, 'description', '')}\n")

    for edge in map.edges:
        print(f"边: {edge.u} -> {edge.v}\n- 名称: {edge.name}\n- 费用: {edge.cost}\n")


__all__ = [
    "load_origin_map_from_json",
    "convert_origin_to_physical_map",
    "convert_origin_to_logical_map",
    "show_map_info",
]