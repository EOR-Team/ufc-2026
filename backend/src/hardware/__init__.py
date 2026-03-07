# src/hardware/__init__.py
# 硬件驱动包
# 在树莓派环境下加载真实驱动；开发机上加载失败时 Robot = None，HARDWARE_AVAILABLE = False

from src.logger import info, warning

try:
    from src.hardware.loborobot import LOBOROBOT, Robot
    HARDWARE_AVAILABLE: bool = True
    info("[Hardware] LOBOROBOT 驱动加载成功")
except Exception as _e:
    LOBOROBOT = None   # type: ignore
    Robot = None       # type: ignore
    HARDWARE_AVAILABLE = False
    warning(f"[Hardware] 硬件驱动不可用（非树莓派环境）: {_e}")

__all__ = ["LOBOROBOT", "Robot", "HARDWARE_AVAILABLE"]
