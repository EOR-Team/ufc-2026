import json
from typing import Any, Callable
from openai import OpenAI

from src.IntegratedSystem.integrated_system import IntegratedSystem
from src.config import general
from src.llm.online.client import get_online_client
import os
from dotenv import load_dotenv

load_dotenv()

client = get_online_client()
system = IntegratedSystem()


def enroll_new_patient(name: str, timeout: float = 30.0) -> dict | None:
    """
    录入新患者（人脸录入 + 创建病历）
    :param name: 患者姓名
    :param timeout: 超时时间
    :return: {"name": name, "id": id} 或 None
    """
    return system.enroll_new_patient(name, timeout)


def recognize_patient(timeout: float = 30.0) -> dict | None:
    """
    通过人脸识别来识别患者
    :param timeout: 超时时间
    :return: {"name": name, "id": id} 或 None
    """
    return system.recognize_patient(timeout)


def add_medical_record(patient_id: int, medical_record: str) -> bool:
    """
    为患者添加病历
    :param patient_id: 患者ID
    :param medical_record: 病历内容
    :return: bool
    """
    return system.add_medical_record(patient_id, medical_record)


def get_patient_info(patient_id: int) -> dict | None:
    """
    获取患者完整信息
    :param patient_id: 患者ID
    :return: 患者信息字典或None
    """
    return system.get_patient_info(patient_id)


def delete_patient(patient_id: int) -> bool:
    """
    删除患者（同时删除人脸和病历）
    :param patient_id: 患者ID
    :return: bool
    """
    return system.delete_patient(patient_id)


TOOLS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "enroll_new_patient",
            "description": "录入新患者（人脸录入 + 创建病历）",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "患者姓名"},
                    "timeout": {"type": "number", "description": "超时时间", "default": 30.0},
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "recognize_patient",
            "description": "通过人脸识别来识别患者",
            "parameters": {
                "type": "object",
                "properties": {
                    "timeout": {"type": "number", "description": "超时时间", "default": 30.0},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_medical_record",
            "description": "为患者添加病历",
            "parameters": {
                "type": "object",
                "properties": {
                    "patient_id": {"type": "integer", "description": "患者ID"},
                    "medical_record": {"type": "string", "description": "病历内容"},
                },
                "required": ["patient_id", "medical_record"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_patient_info",
            "description": "获取患者完整信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "patient_id": {"type": "integer", "description": "患者ID"},
                },
                "required": ["patient_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_patient",
            "description": "删除患者（同时删除人脸和病历）",
            "parameters": {
                "type": "object",
                "properties": {
                    "patient_id": {"type": "integer", "description": "患者ID"},
                },
                "required": ["patient_id"],
            },
        },
    },
]

FUNCTION_MAP: dict[str, Callable] = {
    "enroll_new_patient": enroll_new_patient,
    "recognize_patient": recognize_patient,
    "add_medical_record": add_medical_record,
    "get_patient_info": get_patient_info,
    "delete_patient": delete_patient,
}

SYSTEM_PROMPT = """# 基于人脸识别的智能病历系统 
## 任务说明
你是一个智能病历系统的记录员，负责通过人脸识别技术识别患者，并为其创建和管理病历。
## 可用工具
1. enroll_new_patient(name, timeout=30.0): 录入新患者（人脸录入 + 创建病历）
2. recognize_patient(timeout=30.0): 通过人脸识别来识别患者
3. add_medical_record(patient_id, medical_record): 为患者添加病历
4. get_patient_info(patient_id): 获取患者完整信息
5. delete_patient(patient_id): 删除患者（同时删除人脸和病历）
## 交互格式
- 当有新患者到来时，使用 recognize_patient 工具进行识别。
  - 如果识别成功，获取患者信息并记录病历。
  - 如果识别失败，使用 enroll_new_patient 工具录入新患者信息。
- 使用 add_medical_record 工具为患者添加新的病历信息。
- 使用 get_patient_info 工具获取患者的完整信息。
- 如果患者要求删除其信息，使用 delete_patient 工具。
## 注意事项
- 始终确保患者信息的隐私和安全。
- 在使用任何工具前，确保理解其参数和返回值。
"""


class RecorderAgent:
    def __init__(self, model: str = general.DEFAULT_ONLINE_MODEL):
        self.model = model
        self._messages: list[dict] = []

    def _execute_tool(self, name: str, arguments: dict) -> Any:
        func = FUNCTION_MAP.get(name)
        if not func:
            return {"error": f"Unknown function: {name}"}
        return func(**arguments)

    def _build_messages(self, query: str, context: dict | None = None) -> list[dict]:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if self._messages:
            messages.extend(self._messages)
        if context:
            messages.append({"role": "user", "content": f"上下文信息: {json.dumps(context, ensure_ascii=False)}"})
        messages.append({"role": "user", "content": query})
        return messages

    def run(self, query: str, context: dict | None = None, max_iterations: int = 10) -> dict:
        messages = self._build_messages(query, context)

        for _ in range(max_iterations):
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                temperature=0,
            )

            assistant_message = response.choices[0].message
            messages.append(assistant_message.model_dump(exclude_none=True))

            if not assistant_message.tool_calls:
                self._messages = messages[1:]
                return {
                    "success": True,
                    "response": assistant_message.content or "",
                }

            for tool_call in assistant_message.tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)
                result = self._execute_tool(func_name, func_args)

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result, ensure_ascii=False) if result is not None else "null",
                    }
                )

        return {"success": False, "response": "达到最大迭代次数"}

    def clear_history(self):
        self._messages = []

    def call(self, query: str, context: dict | None = None) -> dict:
        return self.run(query, context, max_iterations=5)


recoder_agent = RecorderAgent()
