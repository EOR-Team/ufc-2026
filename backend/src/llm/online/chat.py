# llm/online/chat.py
# 在线 Chat Model
#

from agents import OpenAIChatCompletionsModel

from src.config import general
from src.llm.online.client import get_online_client


online_chat_model: OpenAIChatCompletionsModel | None = None


def _build_online_chat_model():
    """
    初始化在线聊天模型

    这么做的实际原因是为了避免 在模块导入时就自动初始化**在线模型**，在无网络环境下会直接报错。
    """

    global online_chat_model

    online_chat_model = OpenAIChatCompletionsModel(
        model = general.ONLINE_CHAT_MODEL,
        openai_client = get_online_client(),
    )


def get_online_chat_model() -> OpenAIChatCompletionsModel:
    """获取在线聊天模型实例"""

    global online_chat_model

    if online_chat_model is None:
        _build_online_chat_model()
    
    return online_chat_model


__all__ = [
    "get_online_chat_model",
]
