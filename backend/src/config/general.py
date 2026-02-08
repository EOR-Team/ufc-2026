# config/general.py
# 全局配置文件
#

import multiprocessing
from typing import Literal
from pathlib import Path

# ========== 全局配置 ==========
BACKEND_ROOT_DIR = Path(__file__).parent.parent.parent.resolve()

# ========== 模型配置 ==========

# === 离线 ===

OFFLINE_MODEL_DIR = BACKEND_ROOT_DIR / "model"

OFFLINE_MODEL_TYPES = Literal[
    "qwen2.5-3b",
    "qwen2.5coder-1.5b",
    "qwen2.5coder-3b",
    "qwen3-1.7b",
    "qwen3-4b",
    "qwen3-embed-0.6b"
]

DEFAULT_OFFLINE_CHAT_MODEL: OFFLINE_MODEL_TYPES = "qwen2.5coder-1.5b"

DEFAULT_OFFLINE_EMBED_MODEL: OFFLINE_MODEL_TYPES = "qwen3-embed-0.6b"

OFFLINE_MODEL_HOST = "http://localhost:8080/v1"

OFFLINE_MODEL_CTX_LEN = 4096

OFFLINE_MODEL_THREADS = 4 # or more


# === 在线 ===

ONLINE_MODEL_TYPES = Literal[
    "deepseek-chat",
    "deepseek-reasoner"
]

DEFAULT_ONLINE_MODEL: ONLINE_MODEL_TYPES = "deepseek-chat"

ONLINE_MODEL_HOST = "https://api.deepseek.com/v1"
