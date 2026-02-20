# map/tools.py
# 地图相关工具函数
#

import json
import heapq
from pydantic import ValidationError

from src.config.general import MAP_PATH
from src.map.typedef import *


def load_map_from_str(json_str: str) -> Map | None:
    """
    从JSON字符串加载地图数据

    Args:
        json_str (str): 包含地图数据的JSON字符串

    Returns:
        Map: 加载的地图对象

    Raises:
        ValidationError: 如果JSON数据无效或不符合预期格式
    """
    try:
        data = json.loads(json_str)
        return Map(**data)

    except json.JSONDecodeError as e:
        # raise ValueError(f"无效的JSON格式: {e}")
        return None

    except ValidationError as e:
        # raise ValueError(f"地图数据验证失败: {e}")
        return None


def compute_costs(map: Map) -> None:
    """
    计算地图中每条边的费用（cost）
    TIPS:
    修改变量本身

    Args:
        map (Map): 地图对象
    """

    for edge in map.edges:
        u_node = next((node for node in map.nodes if node.id == edge.u_node), None)
        v_node = next((node for node in map.nodes if node.id == edge.v_node), None)

        if u_node and v_node:
            dx = u_node.x - v_node.x
            dy = u_node.y - v_node.y

            # Manhattan Distance
            edge.cost = int(abs(dx) + abs(dy))


def check_map_validity(map: Map) -> bool:
    """
    检查地图数据的有效性

    Args:
        map (Map): 地图对象

    Returns:
        bool: 如果地图数据有效则返回True，否则返回False
    """

    node_ids = {node.id for node in map.nodes}

    for edge in map.edges:

        # 1. 边的节点必须存在于节点列表中
        if edge.u_node not in node_ids or edge.v_node not in node_ids:
            return False
        
        # 2. 边的费用必须为正整数 (假设费用已经计算过) 不能有 None Cost
        if edge.cost is None or edge.cost <= 0:
            return False

    return True


def get_all_main_node_ids(map: Map) -> list[str] | None:
    """
    获取地图中所有主节点的ID列表

    Args:
        map (Map): 地图对象

    Returns:
        list[str] | None: 主节点ID列表，如果没有主节点则返回None
    """

    main_node_ids = [node.id for node in map.nodes if node.type == "main"]

    return main_node_ids if main_node_ids else None


def get_all_main_node_id_to_name_and_description(map: Map) -> dict[str, dict[str, str]] | None:
    """
    获取地图中所有主节点的ID、名称和描述的字典

    Args:
        map (Map): 地图对象

    Returns:
        dict[str, dict[str, str]] | None: 主节点ID到名称和描述的字典，如果没有主节点则返回None
    """

    main_node_info = {node.id: {"name": node.name or "", "description": node.description or ""} for node in map.nodes if node.type == "main"}

    return main_node_info if main_node_info else None


def dijkstra_search(
    start_node_id: str,
    end_node_id: str,
    map: Map
) -> list[str] | None:
    """
    使用Dijkstra算法在地图中查找从起始节点到结束节点的最短路径

    Args:
        start_node_id (str): 起始节点ID
        end_node_id (str): 结束节点ID
        map (Map): 地图对象

    Returns:
        list[str] | None: 最短路径上的节点ID列表，如果没有路径则返回None
    """

    # 构建邻接表
    adjacency_list = {}
    for edge in map.edges:
        adjacency_list.setdefault(edge.u_node, []).append((edge.v_node, edge.cost))
        adjacency_list.setdefault(edge.v_node, []).append((edge.u_node, edge.cost))

    # 初始化Dijkstra算法的数据结构
    min_heap = [(0, start_node_id)]  # (累计费用, 节点ID)
    distances = {node.id: float("inf") for node in map.nodes}
    distances[start_node_id] = 0
    previous_nodes: dict[str, str | None] = {node.id: None for node in map.nodes}

    while min_heap:
        current_distance, current_node_id = heapq.heappop(min_heap)

        # 如果到达终点，构建路径
        if current_node_id == end_node_id:
            path = []
            while current_node_id is not None:
                path.append(current_node_id)
                current_node_id = previous_nodes[current_node_id]
            return path[::-1]  # 反转路径

        # 跳过已经找到更短路径的节点
        if current_distance > distances[current_node_id]:
            continue

        # 遍历邻居节点
        for neighbor_id, cost in adjacency_list.get(current_node_id, []):
            distance = current_distance + cost

            # 如果找到更短路径，更新数据结构
            if distance < distances[neighbor_id]:
                distances[neighbor_id] = distance
                previous_nodes[neighbor_id] = current_node_id
                heapq.heappush(min_heap, (distance, neighbor_id))

    return None  # 如果没有路径则返回None


def translate_graph_to_tree(map: Map, root_node_id: str) -> TreeNode | None:
    """
    将地图图结构转换为树结构

    Args:
        map (Map): 地图对象
        root_node_id (str): 树的根节点ID

    Returns:
        TreeNode | None: 转换后的树的根节点 如果根节点不存在则返回None
    """

    node_dict = {node.id: node for node in map.nodes}
    edge_dict = {}
    for edge in map.edges:
        edge_dict.setdefault(edge.u_node, []).append(edge.v_node)
        edge_dict.setdefault(edge.v_node, []).append(edge.u_node)

    if root_node_id not in node_dict:
        return None

    visited = set()
    def build_tree(node_id: str) -> TreeNode:
        visited.add(node_id)
        tree_node = TreeNode(**node_dict[node_id].dict())
        for neighbor_id in edge_dict.get(node_id, []):
            if neighbor_id not in visited:
                tree_node.children.append(build_tree(neighbor_id))
        return tree_node

    return build_tree(root_node_id)


def validate_path(map: Map, path: list[str]) -> bool:
    """
    验证给定路径是否在地图中联通

    Args:
        map (Map): 地图对象
        path (list[str]): 节点ID列表，表示路径
    
    Returns:
        bool: 如果路径有效且联通则返回True，否则返回False
    """

    if not path or check_map_validity(map) is False:
        # 路径为空或地图无效 则路径无效
        return False
    
    root_node = translate_graph_to_tree(map, path[0])

    if root_node is None:
        # 根节点不存在 则路径无效
        return False

    current_node = root_node
    for node_id in path[1:]:
        # 在当前节点的子节点中查找下一个节点
        next_node = next((child for child in current_node.children if child.id == node_id), None)
        if next_node is None:
            # 如果当前节点没有下一个节点 则路径无效
            return False
        current_node = next_node
    
    return True


# 直接在这里加载
with open(MAP_PATH, "r", encoding="utf-8") as f:
    map_json_str = f.read()
    map = load_map_from_str(map_json_str)

main_node_ids = get_all_main_node_ids(map) if map else None
main_node_id_to_name_and_description = get_all_main_node_id_to_name_and_description(map) if map else None
clinic_id_to_name_and_description = {node.id: {"name": node.name or "", "description": node.description or ""} for node in map.nodes if node.id.find("clinic") != -1} if map else None


__all__ = [
    "map",
    "main_node_ids",
    "main_node_id_to_name_and_description",
    "clinic_id_to_name_and_description",
    "load_map_from_str",
    "compute_costs",
    "check_map_validity",
    "get_all_main_node_ids",
    "dijkstra_search",
    "translate_graph_to_tree",
    "validate_path",
]
