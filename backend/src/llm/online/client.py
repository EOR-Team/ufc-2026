# llm/online/client.py
# 在线模型的 AsyncOpenAI client
#

import os
from dotenv import load_dotenv
load_dotenv() # 加载环境变量

from openai import AsyncOpenAI
from agents import set_tracing_disabled

from src.config import general


set_tracing_disabled(True)  # 禁用 tracing 功能
online_client: AsyncOpenAI | None = None


def _build_online_client():
    """
    初始化在线模型的 AsyncOpenAI client

    这么做的实际原因是为了避免 在模块导入时就自动初始化**AsyncOpenAI**，在无网络环境下会直接报错。
    """

    global online_client

    online_client = AsyncOpenAI(
        base_url = general.ONLINE_MODEL_HOST,
        api_key = os.getenv("API_KEY"),
        timeout=300,
    )


def get_online_client() -> AsyncOpenAI:
    """获取在线模型的 AsyncOpenAI client 实例"""

    global online_client

    if online_client is None:
        _build_online_client()
    
    return online_client


__all__ = [
    "get_online_client",
]
