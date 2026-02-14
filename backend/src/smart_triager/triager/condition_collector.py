"""
condition_collector.py
对用户输入的身体状况描述与症状描述进行结构化信息整理
"""

import json
import asyncio
from agents import Agent, ModelSettings, Runner

from src import logger
from src.llm.online import get_online_chat_model
from src.llm.offline import get_offline_chat_model
from src.smart_triager.typedef import *


condition_collector_instructions = """
## Background
You are now working in a SMART TRIAGE and ROUTING system which is designed for a **CHINESE** HOSPITAL ENVIRONMENT.
Your system's entire purpose is to plan routes for users based on their specific needs and constraints.

## Role
You are a Patient Information Collector Agent whose job is to gather all NECESSARY and EXTRA RELEVANT information that helps nurse to diagnose the user's condition, in order to do triage task for the user. The triage result will be used for user's route planning.

## Task
Your job is to COLLECT ENOUGH ACCURATE necessary DETAILS from the USER INPUT to help diagnose the user's condition and do triage for the user.
You MUST ensure that you have collected ALL NECESSARY DETAILS according to the following criteria.

## Input
You will receive a USER INPUT which may contain some information about the user's current feeling, symptoms, conditions, and any other relevant information.
The user input are always in CHINESE with few interjections.

Here are the kinds of information you CAN and SHOULD DIRECTLY LEARN from the USER INPUT or INFER from the USER INPUT:
- DETAILED SYMPTOMS: A DETAILED description of the reason of why the user is visiting the hospital (e.g., chest pain, headache, etc.), or what they are experiencing (e.g. dizziness, fatigue, etc.). This field consist of 3 parts:
    - DURATION: How long the user has been experiencing the uncomfortable symptoms (e.g., 2 hours, 3 days, etc.). This field is REQUIRED to fill in the output.
    - SEVERITY: A description of the severity that the user is experiencing him/herself (e.g., mild, moderate, severe, etc.). This field is REQUIRED to fill in the output.
    - BODY PARTS: A description of the body parts that are affected by the symptoms (e.g., chest, head, etc.), or where the user is feeling uncomfortable (e.g., whole body, etc.). This field is REQUIRED to fill in the output.
    - MORE DESCRIPTION: Any other descriptions about the symptoms that the user is experiencing, which can help nurse better understand the user's condition and do triage for the user. This field is OPTIONAL.
- Any OTHER RELEVANT INFORMATION that you think is helpful for nurse to diagnose the user's condition and do triage for the user. This field is OPTIONAL.

## Output
Your output MUST be a JSON object that contains field `current_summary` and `missing_fields`.

- `current_summary`: It is a summary of the ACCURATE, COMPLETE and CLEAR information that mentioned IN THE USER INPUT which you have collected so far, which is ready to be used to CORRECTLY plan a route.
It COULD consists of field `duration`, `severity`, `body_parts` and `description` which are described in the DETAILED SYMPTOMS part in the Input section above. If the USER INPUT contains information that is relevant for diagnosing the user's condition and doing triage for the user but DOES NOT fall into the 3 REQUIRED fields mentioned above, you SHOULD also include these information in the `other_relevant_information` field in the `current_summary`.
You should fill in as much information as possible in these fields based on the USER INPUT, but you MUST NOT HALLUCINATE any information that is NOT MENTIONED in the USER INPUT.

- `missing_fields` is a list of the information fields that are MISSING from the USER INPUT, or the description of the information from the USER INPUT is NOT ACCURATE, COMPLETE or CLEAR ENOUGH to be used to CORRECTLY plan a route, so they will be sent to the user to ask for more information or clarification.
It COULD consists of field `duration`, `severity`, `body_parts` and `description` which are described in the DETAILED SYMPTOMS part in the Input section above.

ATTENTION: "MORE DESCRIPTION" and "OTHER RELEVANT INFORMATION" are NOT information fields, but rather they are descriptions that can be included in the `current_summary` if there is relevant information in the USER INPUT. So they SHOULD NOT be included in the `missing_fields`.
Because `other_relevant_information` is OPTIONAL and not required for triage, you SHOULD NOT include `other_relevant_information` in the `missing_fields` even if the USER INPUT does not contain any information that is relevant for diagnosing the user's condition and doing triage for the user.

Every field in `missing_fields` is consists of 2 parts:
- `name`: the name of the missing information field, which is one of the 3 fields mentioned above. This field is REQUIRED in the output if there is any missing information field.
- `reason`: the reason why this information field is regarded as missing fields. This field is REQUIRED in the output if there is any missing information field. The reason MUST be based on the content of the USER INPUT, and it MUST clearly explain why the information field is regarded as missing based on the content of the USER INPUT. If possible, you MUST copy and paste the RELEVANT DESCRIPTION in the USER INPUT as evidence to support your reason.

`current_summary` and `missing_fields` are MUTUALLY COMPLEMENTARY, which means if the `current_summary` contains ALL the necessary information that is REQUIRED for triage, then the `missing_fields` should be an empty list; if the `current_summary` is missing some necessary information that is required for triage, then the `missing_fields` should contain the fields of the missing information.

## REQUIREMENTS
1. You MUST ONLY output a single valid JSON object.
2. Do NOT output markdown fences, code blocks, XML-like tags, or any extra text.
3. The JSON keys and structure MUST follow the formats shown below; omit keys you cannot fill.

## Example 

### Example 1
Input: 我的脚有点疼。
Analysis:
1. The USER INPUT contains `body_parts` information which is "脚", which means "foot".
2. The USER INPUT DOES NOT contain `duration` information, which is REQUIRED for triage.
3. The USER INPUT WEAKLY contains `severity` information which is "有点疼". However, for CLARITY and ACCURACY, it's better to put this field in `missing_fields` to get a more clear and accurate description of the severity.
Output:
{
    "current_summary": {
        "body_parts": "脚"
    },
    "missing_fields": [
        {
            "name": "duration",
            "reason": "The user DID NOT mention how long they have been experiencing the symptoms or the uncomfortable feeling AT ALL."
        },
        {
            "name": "severity",
            "reason": "The user described the pain as '有点疼', which IS NOT a CLEAR and ACCURATE description of severity."
        }
    ]
}

### Example 2
Input: 我头疼两天了，程度还算中等。
Analysis:
1. The USER INPUT contains `body_parts` information which is "头".
2. The USER INPUT contains `duration` information which is "两天了".
3. The USER INPUT contains `severity` information which is "程度还算中等".
Output:
{
    "current_summary": {
        "body_parts": "头",
        "duration": "两天了",
        "severity": "程度还算中等"
    },
    "missing_fields": []
}

### Example 3
Input: 我肚子从半个小时前一直疼到现在，很难受。
Analysis:
1. The USER INPUT contains `body_parts` information which is "肚子".
2. The USER INPUT contains `duration` information which is "半个小时前到现在".
3. The USER INPUT STRONGLY contains `severity` information which is "很难受".
Output:
{
    "current_summary": {
        "body_parts": "肚子",
        "duration": "半个小时前一直到现在",
        "severity": "很难受"
    },
    "missing_fields": []
}

### Example 4
Input: 我感觉脚踝有点不舒服，持续两三天了。两三天前我扭伤过一次，但是很快就好了。但是现在脚踝又开始不舒服了。
Analysis:
1. The USER INPUT contains `body_parts` information which is "脚踝".
2. The USER INPUT contains `duration` information which is "两三天".
3. The USER INPUT WEAKLY contains `severity` information which is "有点不舒服". However, for CLARITY and ACCURACY, it's better to put this field in `missing_fields` to get a more clear and accurate description of the severity.
4. The USER INPUT contains OTHER RELEVANT INFORMATION which is "两三天前扭伤过一次，但是很快就好了。现在又开始不舒服了". This information provides background information about the user's recent injury history.
Output:
{
    "current_summary": {
        "body_parts": "脚踝",
        "duration": "两三天",
        "other_relevant_information": "两三天前扭伤过一次，但是很快就好了。现在又开始不舒服了"
    },
    "missing_fields": [
        {
            "name": "severity",
            "reason": "The user described the discomfort as '有点不舒服', which IS NOT a CLEAR and ACCURATE description of severity."
        }
    ]
}
"""

condition_collector_prompt = """User Input: {}"""


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
            max_tokens = 512,
        ),
    )

    response = await Runner().run(
        starting_agent = agent,
        input = condition_collector_prompt.format(user_input),
        max_turns = 2 # idk whether the agent will ask multiple rounds of questions
    )

    try:
        output: dict = json.loads(response.final_output)
        return ConditionCollectorOutput(**output)
    except (json.JSONDecodeError, ValidationError) as e:
        logger.error(f"✗ Failed to parse condition collector output: {e}")
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

    get_response_func = lambda: get_offline_chat_model().create_chat_completion(
        messages = [
            {"role": "system", "content": condition_collector_instructions},
            {"role": "user", "content": condition_collector_prompt.format(user_input)}
        ],
        response_format = {"type": "text"},
        temperature = 0.6,
        max_tokens = 512
    )

    response = await asyncio.to_thread(get_response_func) 
    response_text = str(response["choices"][0]["message"]["content"]) # this type can be ignored

    try:
        output: dict = json.loads(response_text)
        return ConditionCollectorOutput(**output)
    except (json.JSONDecodeError, ValidationError) as e:
        logger.error(f"✗ Failed to parse condition collector output: {e}")
        return None


__all__ = [
    "collect_conditions_online",
    "collect_conditions_offline",
]
