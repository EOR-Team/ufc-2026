import json
from typing import Any, Callable

from src.IntegratedSystem.integrated_system import IntegratedSystem
from src.config import general
from src.llm.online.client import get_online_client
from src import utils
from dotenv import load_dotenv

load_dotenv()

client = get_online_client()
system = IntegratedSystem()


def enroll_new_patient(name: str, image_path: str | None = None) -> dict | None:
    """
    录入新患者（从静态图片录入人脸并创建病历）
    :param name: 患者姓名
    :param image_path: 可选图片路径（默认使用 backend/assets/face/face.png）
    :return: {"name": name, "id": id} 或 None
    """
    return system.enroll_new_patient(name, image_path)


def recognize_patient(image_path: str | None = None) -> dict | None:
    """
    通过静态图片进行人脸识别并返回患者信息
    :param image_path: 可选图片路径（默认使用 backend/assets/face/face.png）
    :return: {"name": name, "id": id} 或 None
    """
    return system.recognize_patient(image_path)


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
            "description": "录入新患者（从静态图片录入人脸并创建病历）",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "患者姓名"},
                    "image_path": {"type": "string", "description": "可选图片路径，默认 backend/assets/face/face.png"},
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "recognize_patient",
            "description": "通过静态图片来识别患者（默认 backend/assets/face/face.png）",
            "parameters": {
                "type": "object",
                "properties": {
                    "image_path": {"type": "string", "description": "可选图片路径，默认 backend/assets/face/face.png"},
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
1. enroll_new_patient(name, image_path=None): 从静态图片录入新患者（默认 backend/assets/face/face.png）
2. recognize_patient(image_path=None): 通过静态图片来识别患者（默认 backend/assets/face/face.png）
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
        messages = [{"role": "system", "content": utils.instruction_token_wrapper(SYSTEM_PROMPT)}]
        if self._messages:
            messages.extend(self._messages)
        if context:
            messages.append({"role": "user", "content": utils.input_token_wrapper(f"上下文信息: {json.dumps(context, ensure_ascii=False)}")})
        messages.append({"role": "user", "content": utils.input_token_wrapper(query)})
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


# --- 对外包装函数（供其他 AI/模块调用） ---
def create_recorder_agent(model: str | None = None) -> RecorderAgent:
    """
    创建并返回一个新的 `RecorderAgent` 实例。
    :param model: 可选模型名称，默认为配置中的 `DEFAULT_ONLINE_MODEL`
    """
    return RecorderAgent(model or general.DEFAULT_ONLINE_MODEL)


def run_recorder_agent(query: str, context: dict | None = None, max_iterations: int = 10, agent: RecorderAgent | None = None) -> dict:
    """
    使用 RecorderAgent 运行一个多轮对话（允许工具调用）。
    :param query: 用户查询文本
    :param context: 可选上下文字典
    :param max_iterations: 最大迭代次数（工具交互轮数）
    :param agent: 可选的 RecorderAgent 实例，未提供时使用模块级 `recoder_agent`
    :return: 运行结果字典，包含 success/response 或工具返回内容
    """
    ag = agent or recoder_agent
    return ag.run(query, context, max_iterations=max_iterations)


def call_recorder_agent(query: str, context: dict | None = None, agent: RecorderAgent | None = None) -> dict:
    """
    快速单次调用（短循环）接口，等价于 `RecorderAgent.call`。
    :param query: 用户查询文本
    :param context: 可选上下文
    :param agent: 可选 RecorderAgent 实例
    """
    ag = agent or recoder_agent
    return ag.call(query, context)


def execute_tool(name: str, arguments: dict) -> Any:
    """
    直接执行注册在本模块的工具函数（供其他 AI 调用）。
    :param name: 工具名（例如 "recognize_patient"）
    :param arguments: 函数参数字典
    :return: 工具执行结果
    """
    func = FUNCTION_MAP.get(name)
    if not func:
        return {"error": f"Unknown function: {name}"}
    return func(**arguments)


def get_tools_spec() -> list[dict]:
    """
    返回可用工具的规范（TOOL 描述列表），便于上层 AI 动态查询工具能力。
    """
    return TOOLS
