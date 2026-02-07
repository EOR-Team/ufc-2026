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

from src import config


set_tracing_disabled(True)  # 禁用 tracing 功能

online_client = AsyncOpenAI(
    base_url = config.ONLINE_MODEL_HOST,
    api_key = os.getenv("API_KEY", ""),
)

online_model = OpenAIChatCompletionsModel(
    model = config.ONLINE_MODEL,
    openai_client = online_client,
)