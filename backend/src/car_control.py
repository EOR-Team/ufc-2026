# car_control.py
# 小车控制模块，实现基础的小车控制功能
# 通过 LOBOROBOT.Robot 单例驱动真实硬件

import asyncio
from typing import Optional
from pydantic import BaseModel, Field
from src.logger import info, warning, error, debug
from src.smart_triager.car.typedef import CarAction, Orientation

# 1 个地图格子单位对应的真实物理距离（米），实测标定值
UNIT_TO_METERS: float = 0.185

# 尝试导入真实硬件驱动；若不在树莓派上则降级为纯日志模式
try:
    from src.hardware import Robot as _Robot, HARDWARE_AVAILABLE as _HARDWARE_AVAILABLE
except Exception as _e:
    _Robot = None  # type: ignore
    _HARDWARE_AVAILABLE = False
    info(f"[CarControl] 硬件包导入失败，使用模拟模式: {_e}")


class CarController:
    """
    小车控制器类，提供基础的小车控制方法
    当前为留空实现，仅记录日志，实际硬件集成需根据具体硬件平台实现
    """

    def __init__(self, car_id: str = "default_car"):
        """
        初始化小车控制器

        Args:
            car_id: 小车标识符，用于日志记录
        """
        self.car_id = car_id
        info(f"CarController initialized for car: {car_id}")

    async def forward(self, distance: float) -> bool:
        """
        控制小车前进指定距离（格子单位，内部自动换算为米）
        """
        meters = distance * UNIT_TO_METERS
        info(f"[{self.car_id}] Forward: {distance} units = {meters:.3f}m")
        if _HARDWARE_AVAILABLE:
            await _Robot.forward(meters)
        else:
            await asyncio.sleep(0.1)  # 模拟
        return True

    async def backward(self, distance: float) -> bool:
        """
        控制小车后退指定距离（格子单位，内部自动换算为米）
        """
        meters = distance * UNIT_TO_METERS
        info(f"[{self.car_id}] Backward: {distance} units = {meters:.3f}m")
        if _HARDWARE_AVAILABLE:
            await _Robot.backward(meters)
        else:
            await asyncio.sleep(0.1)  # 模拟
        return True

    async def left(self) -> bool:
        """
        控制小车左转90度
        """
        info(f"[{self.car_id}] Turn left 90°")
        if _HARDWARE_AVAILABLE:
            await _Robot.turn_left(90)
        else:
            await asyncio.sleep(0.1)  # 模拟
        return True

    async def right(self) -> bool:
        """
        控制小车右转90度
        """
        info(f"[{self.car_id}] Turn right 90°")
        if _HARDWARE_AVAILABLE:
            await _Robot.turn_right(90)
        else:
            await asyncio.sleep(0.1)  # 模拟
        return True

    async def stop(self) -> bool:
        """
        控制小车停止
        """
        info(f"[{self.car_id}] Stop")
        if _HARDWARE_AVAILABLE:
            _Robot._bot.t_stop()
        else:
            await asyncio.sleep(0.05)  # 模拟
        return True

    async def execute_action(self, action: CarAction) -> bool:
        """
        执行单个CarAction指令

        Args:
            action: CarAction对象，包含转向和移动距离信息

        Returns:
            bool: 执行是否成功

        Raises:
            ValueError: 如果action无效
        """
        if action.distance < 0:
            raise ValueError(f"Invalid distance: {action.distance}, must be >= 0")

        info(f"[{self.car_id}] Executing CarAction: orientation={action.orientation}, distance={action.distance:.3f}m")

        # 执行转向（如果需要）
        if action.orientation == Orientation.left:
            await self.left()
        elif action.orientation == Orientation.right:
            await self.right()
        # straight不需要额外转向

        # 执行移动（如果距离>0）
        if action.distance > 0:
            await self.forward(action.distance)

        info(f"[{self.car_id}] CarAction execution completed successfully")
        return True

    async def execute_actions_sequence(self, actions: list[CarAction]) -> list[bool]:
        """
        按顺序执行一系列CarAction指令

        Args:
            actions: CarAction列表

        Returns:
            list[bool]: 每个指令的执行结果列表
        """
        if not actions:
            info(f"[{self.car_id}] No actions to execute")
            return []

        info(f"[{self.car_id}] Starting execution of {len(actions)} actions sequence")
        results = []

        for i, action in enumerate(actions):
            info(f"[{self.car_id}] Executing action {i+1}/{len(actions)}: {action.orientation}, distance={action.distance}")
            try:
                result = await self.execute_action(action)
                results.append(result)
                info(f"[{self.car_id}] Action {i+1} executed successfully")
            except Exception as e:
                error(f"[{self.car_id}] Failed to execute action {i+1}: {e}")
                results.append(False)
                # 可以选择继续执行后续动作或停止
                # 当前实现：记录错误并继续执行
                warning(f"[{self.car_id}] Continuing with next action despite failure")

        success_count = sum(1 for r in results if r)
        info(f"[{self.car_id}] Actions sequence completed: {success_count}/{len(actions)} successful")
        return results


# 全局小车控制器实例（单例模式）
_global_car_controller: Optional[CarController] = None


def get_car_controller(car_id: str = "default_car") -> CarController:
    """
    获取全局小车控制器实例（单例模式）

    Args:
        car_id: 小车标识符

    Returns:
        CarController: 小车控制器实例
    """
    global _global_car_controller

    if _global_car_controller is None:
        _global_car_controller = CarController(car_id)
        info(f"Global CarController instance created with car_id: {car_id}")

    return _global_car_controller


async def execute_car_action(action: CarAction, car_id: str = "default_car") -> bool:
    """
    便捷函数：执行单个小车动作

    Args:
        action: CarAction对象
        car_id: 小车标识符

    Returns:
        bool: 执行是否成功
    """
    controller = get_car_controller(car_id)
    return await controller.execute_action(action)


async def execute_car_actions_sequence(actions: list[CarAction], car_id: str = "default_car") -> list[bool]:
    """
    便捷函数：执行一系列小车动作

    Args:
        actions: CarAction列表
        car_id: 小车标识符

    Returns:
        list[bool]: 每个指令的执行结果列表
    """
    controller = get_car_controller(car_id)
    return await controller.execute_actions_sequence(actions)


# Pydantic模型用于API响应
class CarControlResponse(BaseModel):
    """小车控制API响应模型"""
    success: bool = Field(..., description="控制是否成功")
    message: str = Field(..., description="响应消息")
    action_index: Optional[int] = Field(None, description="动作索引（如果执行多个动作）")
    car_id: str = Field(..., description="小车标识符")


__all__ = [
    "CarController",
    "get_car_controller",
    "execute_car_action",
    "execute_car_actions_sequence",
    "CarControlResponse",
]