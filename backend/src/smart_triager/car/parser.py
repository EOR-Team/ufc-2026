# smart_triager/car/parser.py
# 路径解析和指令生成

from typing import Optional
from src.map import Map, dijkstra_search
from src.smart_triager.typedef import LocationLink
from .typedef import Orientation, CarAction, CarCommandsOutput


def expand_main_route_to_full_path(
    route: list[LocationLink],
    map: Map
) -> list[str]:
    """
    将只包含main节点的路径扩展为包含nav节点的完整路径

    步骤：
    1. 从第一个LocationLink的this节点开始
    2. 遍历每个LocationLink，对每个this→next对：
       a. 使用dijkstra_search(this, next, map)查找最短路径
       b. 将路径节点加入完整路径（避免重复添加连接点）
    3. 返回完整节点ID列表

    参数:
        route: LocationLink序列，只包含main节点
        map: 地图数据结构

    返回:
        包含main和nav节点的完整节点ID列表

    异常:
        ValueError: 如果路径不存在或输入无效
    """
    if not route:
        return []

    full_path: list[str] = []

    # 处理第一个节点
    first_link = route[0]
    full_path.append(first_link.this)

    # 遍历每个LocationLink
    for link in route:
        # 查找this→next的最短路径
        path = dijkstra_search(link.this, link.next, map)
        if not path:
            raise ValueError(f"No path found between {link.this} and {link.next}")

        # 添加路径节点（跳过第一个节点，避免重复）
        full_path.extend(path[1:])

    return full_path


def get_absolute_direction(dx: int, dy: int) -> str:
    """
    根据坐标差计算绝对方向

    参数:
        dx: x坐标差 (x2 - x1)
        dy: y坐标差 (y2 - y1)

    返回:
        绝对方向字符串: "east", "west", "south", "north", "stay"
    """
    if dx > 0:
        return "east"
    if dx < 0:
        return "west"
    if dy > 0:
        return "south"
    if dy < 0:
        return "north"
    return "stay"  # 相同位置


def get_relative_turn(current_dir: str, target_dir: str) -> Orientation:
    """
    计算从当前方向到目标方向的相对转向

    参数:
        current_dir: 当前绝对方向 ("east", "west", "south", "north")
        target_dir: 目标绝对方向 ("east", "west", "south", "north")

    返回:
        Orientation枚举值: straight, left, right

    注意:
        - 180°转向分解为两个90°转向（返回left或right，调用者需处理）
        - 假设顺时针90°为left，逆时针90°为right
    """
    # 方向角度映射：东=0°, 北=90°, 西=180°, 南=270°
    dir_to_deg = {"east": 0, "north": 90, "west": 180, "south": 270}

    if current_dir not in dir_to_deg or target_dir not in dir_to_deg:
        raise ValueError(f"Invalid direction: current={current_dir}, target={target_dir}")

    deg_diff = (dir_to_deg[target_dir] - dir_to_deg[current_dir]) % 360

    if deg_diff == 0:
        return Orientation.straight
    elif deg_diff == 90:
        return Orientation.left  # 顺时针90°为左转
    elif deg_diff == 270:
        return Orientation.right  # 逆时针90°为右转
    elif deg_diff == 180:
        # 180°转向，默认分解为两个左转（调用者需处理）
        return Orientation.left
    else:
        raise ValueError(f"Unexpected angle difference: {deg_diff}°")


def merge_straight_moves(actions: list[CarAction]) -> list[CarAction]:
    """
    合并连续的straight动作

    参数:
        actions: CarAction列表

    返回:
        合并后的CarAction列表
    """
    if not actions:
        return []

    merged: list[CarAction] = []
    for action in actions:
        if (action.orientation == Orientation.straight and
            merged and
            merged[-1].orientation == Orientation.straight):
            # 合并连续的straight动作
            merged[-1].distance += action.distance
        else:
            merged.append(action)

    return merged


def parse_route_to_commands(
    route: list[LocationLink],
    map: Map
) -> CarCommandsOutput:
    """
    将LocationLink路径转换为小车移动指令

    两阶段处理：
    1. 路径扩展：main节点 → 完整路径（包含nav节点）
    2. 指令生成：完整路径 → CarAction序列

    参数:
        route: LocationLink序列，只包含main节点
        map: 地图数据结构

    返回:
        CarCommandsOutput对象，包含小车动作序列

    异常:
        ValueError: 如果输入无效或路径处理失败
    """
    # 阶段1：路径扩展
    full_path = expand_main_route_to_full_path(route, map)

    if len(full_path) < 2:
        # 路径至少需要两个节点
        return CarCommandsOutput(actions=[])

    # 阶段2：指令生成

    # 1. 获取节点坐标字典
    node_dict = {node.id: node for node in map.nodes}

    # 2. 计算绝对方向序列和距离
    directions: list[str] = []
    distances: list[int] = []

    for i in range(len(full_path) - 1):
        node_id1 = full_path[i]
        node_id2 = full_path[i + 1]

        node1 = node_dict.get(node_id1)
        node2 = node_dict.get(node_id2)

        if not node1 or not node2:
            raise ValueError(f"Node not found: {node_id1} or {node_id2}")

        dx = int(node2.x - node1.x)  # 坐标转换为整数
        dy = int(node2.y - node1.y)

        direction = get_absolute_direction(dx, dy)
        distance = abs(dx) + abs(dy)  # 曼哈顿距离

        directions.append(direction)
        distances.append(distance)

    # 3. 转换为相对转向序列，合并转向与后续直线段
    actions: list[CarAction] = []

    for i in range(len(directions)):
        if i == 0:
            # 第一个线段：总是straight（无前置转向）
            orientation = Orientation.straight
        else:
            # 计算从前一线段方向到当前方向的转向
            orientation = get_relative_turn(directions[i-1], directions[i])

        # 创建动作：转向 + 当前线段的距离
        action = CarAction(orientation=orientation, distance=distances[i])
        actions.append(action)

    # 4. 合并连续的straight移动
    merged_actions = merge_straight_moves(actions)

    # 5. 清理：移除distance=0的动作（纯转向且无后续移动的情况）
    final_actions = [action for action in merged_actions if action.distance > 0]

    return CarCommandsOutput(actions=final_actions)