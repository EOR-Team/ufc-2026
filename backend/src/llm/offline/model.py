# llm/offline/model.py
# 本地 Model
#

from openai import AsyncOpenAI
from agents import (
    set_tracing_disabled,
    OpenAIChatCompletionsModel,
)

from src import config
    

set_tracing_disabled(True)  # 禁用 tracing 功能

offline_client = AsyncOpenAI(
    base_url = config.OFFLINE_MODEL_HOST,
    api_key = "sk-xxx", # LocalLLM 服务不需要 API Key
)

offline_model = OpenAIChatCompletionsModel(
    model = "", # 使用本地 LLM 服务时，模型名称可以留空
    openai_client = offline_client
)
