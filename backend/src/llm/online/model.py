# llm/online/model.py
# 在线 Model
#

import os
import asyncio
from dotenv import load_dotenv
load_dotenv() # 加载环境变量

from openai import AsyncOpenAI
from agents import (
    set_tracing_disabled,
    OpenAIChatCompletionsModel,
    Runner,
    Agent,
    function_tool,
    WebSearchTool
)

from src.config import general


set_tracing_disabled(True)  # 禁用 tracing 功能

online_client = AsyncOpenAI(
    base_url = general.ONLINE_MODEL_HOST,
    api_key = general.ONLINE_MODEL_API,
    timeout=30.0,
)

online_model = OpenAIChatCompletionsModel(
    model = general.DEFAULT_ONLINE_MODEL,
    openai_client = online_client,
)

class OnlineAgent:
    def __init__(self,name = "",instructions = ""):
        self.agent = Agent(
            name = name,
            instructions = instructions,
            model = online_model,
            tools = [],
        )
        self.is_running = False
        self.messages = []
    async def run(self):
        """简洁交互循环：从 stdin 读用户输入，打印并保存模型回复。
        - 输入 `exit()` 退出并返回 ("user_exit", None)
        - 模型有非截断停止原因或有 final_output 时返回 (reason, output)
        """
        self.is_running = True
        try:
            while True:
                user_input = await asyncio.get_event_loop().run_in_executor(None, input, "User: ")
                if isinstance(user_input, str) and user_input.strip() == "exit()":
                    return ("user_exit", None)

                self.messages.append({"role": "user", "content": user_input})

                result = await Runner().run(self.agent, self.messages)

                # 提取回复文本
                assistant_text = getattr(result, "final_output", None) or ""
                if not assistant_text:
                    try:
                        last_raw = result.raw_responses[-1]
                        if isinstance(last_raw, dict):
                            assistant_text = last_raw.get("text") or last_raw.get("content") or ""
                        else:
                            assistant_text = getattr(last_raw, "text", None) or getattr(last_raw, "content", None) or ""
                    except Exception:
                        assistant_text = ""

                print(f"ai: {assistant_text}")
                self.messages.append({"role": "assistant", "content": assistant_text})

                # 检查停止原因
                finish_reason = None
                try:
                    last_raw = result.raw_responses[-1]
                    if isinstance(last_raw, dict):
                        finish_reason = last_raw.get("finish_reason") or last_raw.get("reason")
                    else:
                        finish_reason = getattr(last_raw, "finish_reason", None) or getattr(last_raw, "reason", None)
                except Exception:
                    finish_reason = None

                if finish_reason and str(finish_reason).lower() not in ("length", "max_tokens", "response_length_limit"):
                    return (str(finish_reason), result.final_output)

        finally:
            self.is_running = False
    