# llm/online/model.py
# 在线 Model
#

import os
from dotenv import load_dotenv
load_dotenv() # 加载环境变量

from openai import AsyncOpenAI
from agents import (
    set_tracing_disabled,
    OpenAIChatCompletionsModel,
)

from src.config import general


set_tracing_disabled(True)  # 禁用 tracing 功能
online_client: AsyncOpenAI | None = None
online_chat_model: OpenAIChatCompletionsModel | None = None
online_reasoning_model: OpenAIChatCompletionsModel | None = None


def _build_online_models():
    """
    模型初始化

    这么做的实际原因是为了避免 在模块导入时就自动初始化**在线模型**，在无网络环境下会直接报错。
    """

    global online_client, online_chat_model, online_reasoning_model

    online_client = AsyncOpenAI(
        base_url = general.ONLINE_MODEL_HOST,
        api_key = os.getenv("API_KEY"),
        timeout=30.0,
    )

    online_chat_model = OpenAIChatCompletionsModel(
        model = general.ONLINE_CHAT_MODEL,
        openai_client = online_client,
    )

    online_reasoning_model = OpenAIChatCompletionsModel(
        model = general.ONLINE_REASONING_MODEL,
        openai_client = online_client,
    )


def get_online_chat_model() -> OpenAIChatCompletionsModel:
    """获取在线聊天模型实例"""

    if online_chat_model is None:
        _build_online_models()
    
    return online_chat_model


def get_online_reasoning_model() -> OpenAIChatCompletionsModel:
    """获取在线推理模型实例"""

    if online_reasoning_model is None:
        _build_online_models()
    
    return online_reasoning_model


__all__ = [
    "get_online_chat_model",
    "get_online_reasoning_model",
]

    