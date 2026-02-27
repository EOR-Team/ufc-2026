# llm/online/reason.py
# 在线 Reasoning Model
#

from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel

from src.config import general
from src.llm.online.client import get_online_client


online_client: AsyncOpenAI | None = None
online_reasoning_model: OpenAIChatCompletionsModel | None = None


def _build_online_reasoning_model():
    """
    初始化在线推理模型

    这么做的实际原因是为了避免 在模块导入时就自动初始化**在线模型**，在无网络环境下会直接报错。
    """

    global online_client, online_reasoning_model

    online_reasoning_model = OpenAIChatCompletionsModel(
        model = general.ONLINE_REASONING_MODEL,
        openai_client = get_online_client(),
    )


def get_online_chat_model() -> OpenAIChatCompletionsModel:
    """获取在线推理模型实例"""

    global online_reasoning_model

    if online_reasoning_model is None:
        _build_online_reasoning_model()
    
    return online_reasoning_model


__all__ = [
    "get_online_chat_model",
]    
