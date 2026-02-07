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
import heapq

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


def dijkstra_search(
    map_data: OriginMap | PhysicalMap,
    start_node_id: str
) -> dict[str, int]:
    """
    Dijkstra 算法：计算从 start_node_id 到地图中所有其他节点的最短路径开销。
    
    Args:
        map_data (OriginMap | PhysicalMap): 地图数据
        start_node_id (str): 起始节点ID
        
    Returns:
        dict[str, int]: 包含从起点到各个可达节点的最小 cost。
                        例如: {'node_B': 10, 'node_C': 25}
    """
    
    # 1. 构建邻接表 (Adjacency List) 用于加速查找
    #    结构: { 'u_id': [('v_id', cost), ...] }
    adj = {}
    for node in map_data.nodes:
        adj[node.id] = []
    
    for edge in map_data.edges:
        # 确保 edge.cost 已计算
        cost = edge.cost if edge.cost is not None else 1
        # 无向图，双向添加
        if edge.u in adj:
            adj[edge.u].append((edge.v, cost))
        if edge.v in adj:
            adj[edge.v].append((edge.u, cost))
    
    # 2. 初始化
    # 优先队列内容: (当前累计cost, 当前节点id)
    pq = [(0, start_node_id)]
    # 记录最短距离: {节点id: 最小cost}
    distances = {start_node_id: 0}
    
    # 3. 开始扩散
    while pq:
        current_cost, current_node = heapq.heappop(pq)
        
        # 如果当前路径比已记录的短路径长，跳过 (剪枝)
        if current_cost > distances.get(current_node, float('inf')):
            continue
        
        # 遍历邻居
        for neighbor, weight in adj.get(current_node, []):
            distance = current_cost + weight
            
            # 只有发现更短路径时才更新
            if distance < distances.get(neighbor, float('inf')):
                distances[neighbor] = distance
                heapq.heappush(pq, (distance, neighbor))
    
    return distances


def convert_origin_to_logical_map(origin_map: OriginMap) -> LogicalMap:
    """
    将原地图转换为逻辑地图（使用 Dijkstra 算法计算最短路径）

    Args:
        origin_map (OriginMap): 原地图
    Returns:
        LogicalMap: 逻辑地图
    """

    if not check_map_cost(origin_map):
        calculate_all_cost(origin_map)  # 计算所有边的费用

    # 1. 提取所有逻辑节点（主节点，排除导航节点）
    nav_node_ids = {node.id for node in origin_map.nodes if node.type == "nav"}
    logical_nodes = [
        LogicalNode(
            id=node.id,
            name=node.name,
            type=node.type,
            description=node.description,
        ) for node in origin_map.nodes if node.id not in nav_node_ids
    ]

    # 2. 处理特殊情况
    if len(logical_nodes) == 0:
        return LogicalMap(nodes=[], edges=[])  # 无主节点，返回空地图
    if len(logical_nodes) == 1:
        return LogicalMap(nodes=logical_nodes, edges=[])  # 仅有一个主节点，返回无边地图

    # 3. 【核心改进】使用 Dijkstra 构建逻辑边
    logical_edges: list[LogicalEdge] = []

    # 遍历每一个主节点作为起点
    for start_node in logical_nodes:
        # 跑一次 Dijkstra，得到 start_node 到全图所有点的最短距离
        all_distances = dijkstra_search(origin_map, start_node.id)

        # 遍历其他主节点作为终点
        for end_node in logical_nodes:
            if start_node.id == end_node.id:
                continue

            # 检查是否可达
            if end_node.id in all_distances:
                cost = all_distances[end_node.id]
                logical_edges.append(
                    LogicalEdge(
                        u=start_node.id,
                        v=end_node.id,
                        cost=cost
                    )
                )

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
    "dijkstra_search",
]