# config.py
# 全局配置文件

from typing import Literal
from pathlib import Path

# ========== 全局配置 ==========
BACKEND_ROOT_DIR = Path(__file__).parent.parent.resolve()

# ========== 模型配置 ==========

# === 离线 ===

OFFLINE_MODEL_DIR = BACKEND_ROOT_DIR / "model"

OFFLINE_MODEL_TYPES = Literal[
    "qwen2.5-3b",
    "qwen2.5coder-1.5b",
    "qwen2.5coder-3b",
    "qwen3-1.7b",
    "qwen3-4b"
]

OFFLINE_MODEL: OFFLINE_MODEL_TYPES = "qwen2.5coder-1.5b"
