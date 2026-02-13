# config/general.py
# 全局配置文件
#

from typing import Literal
from pathlib import Path


# ========== 全局配置 ==========
BACKEND_ROOT_DIR = Path(__file__).parent.parent.parent.resolve()

# ========== 模型配置 ==========

# === 离线 ===

OFFLINE_MODEL_DIR = BACKEND_ROOT_DIR / "model"

OFFLINE_CHAT_MODEL_PATH = OFFLINE_MODEL_DIR / "qwen2.5-coder-1.5b-instruct-q4_k_m.gguf"
OFFLINE_REASONING_MODEL_PATH = OFFLINE_MODEL_DIR / "Qwen3-4B-Thinking-2507.Q4_K_M.gguf"

# 为本地 llama-cpp-python 服务设置一致的 API Key（如未开启鉴权，可保留占位符）
OFFLINE_MODEL_API_KEY = "sk-xxx"

# === 在线 ===

ONLINE_MODEL_TYPES = Literal[
    "deepseek-chat",
    "deepseek-reasoner"
]

ONLINE_CHAT_MODEL: ONLINE_MODEL_TYPES = "deepseek-chat"

ONLINE_REASONING_MODEL: ONLINE_MODEL_TYPES = "deepseek-reasoner"

ONLINE_MODEL_HOST = "https://api.deepseek.com/v1"
