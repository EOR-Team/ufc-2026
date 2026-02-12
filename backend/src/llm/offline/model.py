# llm/offline/model.py
# 本地 Model
#

from openai import AsyncOpenAI
from agents import (
    set_tracing_disabled,
    OpenAIChatCompletionsModel,
)

from src.config import general
    

set_tracing_disabled(True)  # 禁用 tracing 功能

offline_client = AsyncOpenAI(
    base_url = general.OFFLINE_MODEL_HOST,
    api_key = general.OFFLINE_MODEL_API_KEY, # 与本地服务配置保持一致
)

offline_model = OpenAIChatCompletionsModel(
    model = "", # 使用本地 LLM 服务时，模型名称可以留空
    openai_client = offline_client
)
