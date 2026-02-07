# map/tools.py
# 地图相关工具函数
#
# 包含如下功能
# `check_map_validity`: 检查地图数据是否有效
# `check_map_existance`: 检查地图数据中节点和边是否存在
# `check_map_cost`: 检查地图数据中 cost 是否有效
# `calculate_cost`: 计算两节点之间的费用（曼哈顿距离）
# `calculate_all_cost`: 计算地图中所有边的费用
# `load_origin_map_from_json`: 从 JSON 字符串加载原地图数据
# `convert_origin_to_physical_map`: 将原地图转换为物理地图
# `convert_origin_to_logical_map`: 将原地图转换为逻辑地图
#
# 提醒
# 若地图数据有误，相关函数可能会抛出 AssertionError 或 KeyError
#

import json

from src.map.logical import *
from src.map.physical import *
from src.map.origin import *


def check_map_existance(map: OriginMap | PhysicalMap | LogicalMap) -> bool:
    """
    检查地图数据中节点和边是否存在
    1. 节点列表或边列表为空 -> 无效
    2. 边列表中存在指向不存在的节点 -> 无效

    Args:
        map (OriginMap | PhysicalMap | LogicalMap): 地图

    Returns:
        bool: 是否有效
    """

    #
    if len(map.nodes) == 0 or len(map.edges) == 0:
        # 节点或边列表为空
        return False
    
    u_node_id_set = set(edge.u for edge in map.edges)
    v_node_id_set = set(edge.v for edge in map.edges)
    node_id_set = u_node_id_set.union(v_node_id_set) # 地图中所有边涉及的节点ID集合

    for node in map.nodes:
        if node.id in node_id_set:
            node_id_set.remove(node.id) # 移除存在的节点ID
    
    if len(node_id_set) > 0:
        # 存在指向不存在节点的边
        return False
    
    return True


def check_map_cost(map: OriginMap | PhysicalMap | LogicalMap) -> bool:
    """
    检查地图数据中 cost 是否有效
    若 存在 cost 为 None 或负值则视为无效

    Args:
        map (OriginMap | PhysicalMap | LogicalMap): 地图

    Returns:
        bool: 是否有效
    """

    for edge in map.edges:
        if edge.cost is None or edge.cost < 0:
            return False
    return True


def check_map_validity(map: OriginMap | PhysicalMap | LogicalMap) -> bool:
    """
    检查地图数据是否有效
    包含节点和边是否存在及 cost 是否有效的检查

    Args:
        map (OriginMap | PhysicalMap | LogicalMap): 地图

    Returns:
        bool: 是否有效
    """

    return check_map_existance(map) and check_map_cost(map)


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


def get_cost_between_nodes(
    map: OriginMap | PhysicalMap | LogicalMap,
    u: str,
    v: str
) -> int | None:
    """
    在地图中查找**相邻两节点**之间的费用
    Args:
        map (OriginMap | PhysicalMap | LogicalMap): 地图
        u (str): 起始节点ID
        v (str): 终止节点ID
    Returns:
        int | None: 费用，若不存在则返回 None
    """

    # 查找边
    for edge in map.edges:
        if (edge.u == u and edge.v == v) or (edge.u == v and edge.v == u):
            return edge.cost # 存在则返回费用

    return None # 不存在


def dfs_find_path(
    map: OriginMap | PhysicalMap | LogicalMap,
    current_node: str,
    target_node: str,
    visited: set[str],
) -> list[str] | None:
    """
    使用深度优先搜索在地图中查找从 current_node 到 target_node 的路径（迭代版本）

    Args:
        map (OriginMap | PhysicalMap | LogicalMap): 地图
        current_node (str): 当前节点ID
        target_node (str): 目标节点ID
        visited (set[str]): 已访问节点ID集合

    Returns:
        list[str] | None: 节点ID路径列表，若不存在则返回 None
    """

    # 使用栈存储 (当前节点, 路径) 元组
    stack = [(current_node, [current_node])]
    visited_copy = visited.copy()
    visited_copy.add(current_node)

    while stack:
        node, path = stack.pop()
        
        if node == target_node:
            return path  # 找到目标节点，返回路径

        for edge in map.edges:
            neighbor_node = None
            if edge.u == node:
                neighbor_node = edge.v
            elif edge.v == node:
                neighbor_node = edge.u
            
            if neighbor_node and neighbor_node not in visited_copy:
                visited_copy.add(neighbor_node)
                stack.append((neighbor_node, path + [neighbor_node]))

    return None  # 不存在路径


def convert_origin_to_logical_map(origin_map: OriginMap) -> LogicalMap:
    """
    将原地图转换为逻辑地图

    Args:
        origin_map (OriginMap): 原地图
    Returns:
        LogicalMap: 逻辑地图
    """

    if not check_map_cost(origin_map):
        calculate_all_cost(origin_map) # 计算所有边的费用

    # 对 nav 节点过滤
    nav_node_ids = set()
    for node in origin_map.nodes:
        if node.type == "nav":
            nav_node_ids.add(node.id)
    
    logical_nodes = [
        LogicalNode(
            id=node.id,
            name=node.name,
            type=node.type,
            description=node.description,
        ) for node in origin_map.nodes if node.id not in nav_node_ids
    ]

    # 过滤特殊情况
    if len(logical_nodes) == 0:
        return LogicalMap(nodes=[], edges=[]) # 无主节点，返回空地图
    if len(logical_nodes) == 1:
        return LogicalMap(nodes=logical_nodes, edges=[]) # 仅有一个主节点，返回无边地图

    # 使用双指针法构建边
    index1 = 0
    index2 = 1
    logical_edges: list[LogicalEdge] = []

    while index1 < len(logical_nodes) - 1:
        u_node = logical_nodes[index1]
        v_node = logical_nodes[index2]

        # 使用 DFS 查找路径
        path = dfs_find_path(
            origin_map,
            current_node=u_node.id,
            target_node=v_node.id,
            visited=set()
        )

        if path is None or len(path) < 2:
            # 不存在路径或路径长度异常，跳过该边
            index2 += 1
            if index2 >= len(logical_nodes):
                index1 += 1
                index2 = index1 + 1
            continue

        # 计算路径总费用
        total_cost = 0
        for i in range(len(path) - 1):
            cost = get_cost_between_nodes(origin_map, path[i], path[i + 1])
            assert cost is not None, "路径中存在无效边"
            total_cost += cost

        logical_edges.append(
            LogicalEdge(
                u=u_node.id,
                v=v_node.id,
                # name="",
                cost=total_cost,
            )
        )

        # 移动指针
        index2 += 1
        if index2 >= len(logical_nodes):
            index1 += 1
            index2 = index1 + 1
    
    return LogicalMap(
        nodes=logical_nodes,
        edges=logical_edges,
    )


__all__ = [
    "load_origin_map_from_json",
    "convert_origin_to_physical_map",
    "convert_origin_to_logical_map",
    "check_map_validity",
    "check_map_existance",
    "check_map_cost",
    "calculate_cost",
    "calculate_all_cost",
]