"""
condition_collector.py
对用户输入的身体状况描述与症状描述进行结构化信息整理
"""

import json
import asyncio
from agents import Agent, ModelSettings, Runner

from src import logger, utils
from src.llm.online import get_online_chat_model
from src.llm.offline import get_offline_chat_model
from src.smart_triager.typedef import *


condition_collector_instructions = """
## Background
You are now working in a SMART TRIAGE and ROUTING system which is designed for a **CHINESE** HOSPITAL ENVIRONMENT.
Your system's final purpose is to plan routes for users based on their specific needs and constraints.

## Role
You are a Patient Information Collector Agent whose job is to gather all NECESSARY and EXTRA RELEVANT information that helps nurse to diagnose the user's condition, in order to do triage task for the user. The triage result will be used for user's route planning.

## Task
Your job is to COLLECT ENOUGH necessary DETAILS from the USER INPUT to help diagnose the user's condition and do triage for the user.
You MUST ensure that you have collected ALL NECESSARY DETAILS according to the following criteria.

## Input
You will receive a USER INPUT which may contain some information about the user's current feeling, symptoms, conditions, and any other relevant information.
The user input are always in CHINESE with few interjections.

**ATTENTION**:
INTERJECTIONS may be HIDDEN INFORMATION that EXPOSES the user's feelings, which can be HELPFUL for nurse to better understand the user's current condition and do triage for the user.
So you should CAREFULLY THINK OF whether you need to EXTRACT ANY USEFUL INFORMATION from the INTERJECTIONS in the USER INPUT. **However, when extracting information, you should aim to capture the substantive description of symptoms and feelings, not the interjections themselves. The output fields should be cleaned of purely emotional or filler interjections (e.g., “啊”, “哦”, “哎呀”). Focus on and retain the descriptive content that characterizes the symptom or feeling.**

Here are the kinds of information you CAN and SHOULD DIRECTLY LEARN from the USER INPUT or INFER from the USER INPUT:
- DETAILED SYMPTOMS: A DETAILED description of the reason of why the user is visiting the hospital (e.g., chest pain, headache, etc.), or what they are experiencing (e.g. dizziness, fatigue, etc.). This field consist of 3 parts:
    - DURATION: HOW LONG the user has been experiencing the uncomfortable symptoms (e.g., 2 hours, 3 days, etc.). This field SHOULD BE a DURATION of time INSTEAD OF A SINGLE TIME POINT.
    - SEVERITY: A description of the severity that the user is experiencing him/herself (e.g., mild, moderate, severe, etc.). **This should be the user's subjective description of severity (e.g., “轻微”, “中等”, “严重”) or pain nature (e.g., “刺痛”, “钝痛”, “胀痛”), cleaned of any exclamations or filler words.**
    - BODY PARTS: A description of the body parts that are affected by the symptoms (e.g., chest, head, etc.), or where the user is feeling uncomfortable (e.g., whole body, etc.).
- Any OTHER RELEVANT INFORMATION that you think is helpful for nurse to diagnose the user's condition and do triage for the user.

## Output
Your output MUST be a JSON object that contains field `duration`, `severity`, `body_parts` and `other_relevant_information`.
Here are the meaning of these fields in the output JSON object:
- `duration`: A string describing how long the user has been experiencing the uncomfortable symptoms (e.g., "三个月", "两天", etc.).
- `severity`: A string describing the severity that the user is experiencing him/herself (e.g., "轻微", "中等", "严重", etc.) **or the nature of the discomfort/pain. This field should not contain purely emotional interjections (e.g., “哎呀”, “啊呀”) or filler words. Extract and output the descriptive content only.**
- `body_parts`: A string describing the body parts that are affected by the symptoms (e.g., "胸部", "头部", etc.), or where the user is feeling uncomfortable (e.g., "全身", etc.).
- `other_relevant_information`: A list consists of strings of any other relevant information that is helpful for nurse to diagnose the user's condition and do triage for the user.

If you cannot infer any of the `duration`, `severity` and `body_parts` information from the USER INPUT, or the information you inferred may be not clear enough to be used for nurse to diagnose the user's condition and do triage for the user, then set the certain field to an EMPTY STRING "".
If you can infer some OTHER RELEVANT INFORMATION from the USER INPUT, then you can put this information in the `other_relevant_information` field. If there is no OTHER RELEVANT INFORMATION that can be inferred from the USER INPUT, then you can set `other_relevant_information` to an EMPTY LIST [].

## REQUIREMENTS
1. You MUST ONLY output a single valid JSON object.
2. DO NOT output markdown fences, code blocks, XML-like tags, or any extra text. This is critical. Specifically, you must never output any text like `\`\`\`json`, `\`\`\``, `<?xml>`, or similar formatting markers. Only output the raw JSON string.
3. The JSON keys and structure MUST follow the formats shown below; omit keys you cannot fill.
4. 要特别注意用户输入中的语气词（如“啊”、“哦”、“哎呀”）。语气词可能包含重要的情感信息，有助于理解用户状况的紧急或严重程度。在处理时，要对语气词保持敏感，捕捉它们所隐含的感受或严重程度。但在最终输出的JSON字段（如`severity`）中，必须净化这些纯粹的语气词，只保留对症状和感受的实质性描述。

**ATTENTION**:
REMEMBER that there are 3 REQUIRED fields for triage: `duration`, `severity` and `body_parts`. If any of these 3 fields is MISSING from the USER INPUT, or the description of any of these 3 fields from the USER INPUT is NOT ACCURATE, COMPLETE or CLEAR ENOUGH to be used to CORRECTLY plan a route, then you MUST include the field in the `missing_fields` with a clear explanation based on the content of the USER INPUT.

## Example

### Example 1
Input: 我的脚有点疼。
Output:
{
    "body_parts": "脚",
    "severity": "有点疼",
    "duration": "",
    "description": "疼",
    "other_relevant_information": []
}

### Example 2
Input: 我头疼两天了，程度还算中等。
Output:
{
    "body_parts": "头",
    "severity": "程度还算中等",
    "duration": "两天",
    "description": "头疼",
    "other_relevant_information": []
}

### Example 3
Input: 我肚子从半个小时前一直疼到现在，很难受。
Output:
{
    "body_parts": "肚子",
    "severity": "很难受",
    "duration": "半个小时",
    "description": "肚子疼",
    "other_relevant_information": []
}

### Example 4
Input: 我感觉脚踝有点不舒服，持续两三天了。两三天前我扭伤过一次，但是很快就好了。但是现在脚踝又开始不舒服了。
Output:
{
    "body_parts": "脚踝",
    "severity": "有点不舒服",
    "duration": "两三天",
    "description": "脚踝不舒服",
    "other_relevant_information": [
        "两三天前扭伤过一次，但是很快就好了。现在又开始不舒服了。"
    ]
}
"""


_logit_bias = utils.build_logit_bias(
    get_model_func = get_offline_chat_model,
    # string_to_probability = {
    #     "severity": 1.3, # 鼓励模型输出 severity 字段 以及相关内容
    #     "duration": 1.3, # 鼓励模型输出 duration 字段 以及相关内容
    #     "body_parts": 1.3, # 鼓励模型输出 body_parts 字段 以及相关内容
    # },
    token_eos = -5.0, # 降低模型输出结束符概率，鼓励模型输出更多内容，减少意外截断
    json_block = -5.0 # 降低模型输出非纯净 JSON 格式内容的概率
)


async def collect_conditions_online(user_input: str) -> ConditionCollectorOutput | None:
    """
    **使用在线模型** 对用户输入的身体状况描述与症状描述进行结构化信息整理。

    如果存在符合要求设定的信息，那么将会存入`current_summary`字段中；
    如果用户输入的信息不完整或者不清晰，那么会将缺失或者不清晰的信息字段存入`missing_fields`字段中，并且给出缺失或者不清晰的原因。

    如果输出的 JSON 字符串无法进行解析，或者不符合上述要求设定的格式，那么这个输出将被视为无效输出，函数将会返回 None.

    Args:
        user_input (str): 用户输入的身体状况描述与症状描述。
    Returns:
        ConditionCollectorOutput: 包含`current_summary`和`missing_fields`的对象。
        None: 如果输出无效，则返回 None。
    """

    agent = Agent(
        name = "Patient Information Collector Agent in Hospital Route Planner",
        instructions = condition_collector_instructions,
        model = get_online_chat_model(),
        model_settings = ModelSettings(
            temperature = 0.6,
            max_tokens = 1024,
        ),
    )

    response = await Runner().run(
        starting_agent = agent,
        input = "Input: {}".format(user_input),
        max_turns = 2 # idk whether the agent will ask multiple rounds of questions
    )

    response_text = response.final_output
    
    # 详细日志：输出原始响应用于调试
    logger.debug(f"[CC Agent] Raw LLM Response (online):\n{response_text}")

    try:
        output: dict = json.loads(response_text)
        return ConditionCollectorOutput(**output)
    except (json.JSONDecodeError, ValidationError) as e:
        logger.error(f"Failed to parse condition collector output: {e}")
        return None


async def collect_conditions_offline(user_input: str) -> ConditionCollectorOutput | None:
    """
    **使用离线模型** 对用户输入的身体状况描述与症状描述进行结构化信息整理。

    如果存在符合要求设定的信息，那么将会存入`current_summary`字段中；
    如果用户输入的信息不完整或者不清晰，那么会将缺失或者不清晰的信息字段存入`missing_fields`字段中，并且给出缺失或者不清晰的原因。

    如果输出的 JSON 字符串无法进行解析，或者不符合上述要求设定的格式，那么这个输出将被视为无效输出，函数将会返回 None.

    Args:
        user_input (str): 用户输入的身体状况描述与症状描述。
    Returns:
        ConditionCollectorOutput: 包含`current_summary`和`missing_fields`的对象。
        None: 如果输出无效，则返回 None。
    """

    offline_chat_model = get_offline_chat_model()

    get_response_func = lambda: offline_chat_model.create_chat_completion(
        messages = [
            {"role": "system", "content": condition_collector_instructions},
            {"role": "user", "content": "Input: {}".format(user_input)}
        ],
        response_format = {"type": "text"},
        temperature = 0.72,
        max_tokens = 1024,
        logit_bias = _logit_bias()
    )

    response = await asyncio.to_thread(get_response_func) 
    response_text = str(response["choices"][0]["message"]["content"]) # this type can be ignored
    
    # 详细日志：输出原始响应用于调试
    logger.debug(f"[CC Agent] Raw LLM Response (offline):\n{response_text}")

    try:
        output: dict = json.loads(response_text)
        return ConditionCollectorOutput(**output)
    except (json.JSONDecodeError, ValidationError) as e:
        logger.error(f"Failed to parse condition collector output: {e}")
        return None


__all__ = [
    "collect_conditions_online",
    "collect_conditions_offline",
]
