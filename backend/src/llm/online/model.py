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

    