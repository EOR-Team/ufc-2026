# llm/local/model.py
# 自定义 Model
#

from openai import AsyncOpenAI
from agents import (
    OpenAIChatCompletionsModel,
)

offline_client = AsyncOpenAI(
    base_url = "http://localhost:8080/v1",
    api_key = "sk-xxx", # LocalLLM 服务不需要 API Key
)

offline_model = OpenAIChatCompletionsModel(
    model = "", # 使用本地 LLM 服务时，模型名称可以留空
    openai_client = offline_client
)
