"""
smart_triager/triager/requirement_collector.py
根据用户自述收集患者的具体需求。
"""

import json
import asyncio

from agents import Agent, ModelSettings, Runner

from src import logger, utils
from src.llm.online import get_online_chat_model
from src.llm.offline import get_offline_chat_model
from src.smart_triager.typedef import *

requirement_collector_instructions = """
## Background
You are now working in a SMART TRIAGE and ROUTING system designed for a **CHINESE** HOSPITAL ENVIRONMENT. The system's ultimate goal is to plan routes for users based on their specific needs and constraints.

## Role
You are a Requirement Collector Agent. Your task is to **EXTRACT and COLLECT ALL REQUIREMENTS** present in the user's input. These requirements will be used for the FINAL ROUTE PLANNING. You MUST ensure that you have collected **ALL** requirements and must not miss any.

## Input
You will receive a USER INPUT in **Chinese**, containing requirements that should be applied to the final route. 请确保正确处理中文的语言表达、语法和语义，准确识别需求中的关键信息，避免因语言理解错误导致的需求遗漏或误解。

## Output
Your output MUST be a single valid JSON object containing a `requirements` field, which is a LIST of the user's requirements.
The structure of each requirement in the list is:
- `when`: A string describing the **TIMING** or sequence of the requirement (e.g., "before seeing the doctor", "after getting medicine"). **注意：“when”应专注于时间点或顺序描述（如“现在”、“在...之前”、“在...之后”、“最后”），不包含具体行动。描述应保持简洁，并使用正式、标准的表达，避免口语化。**
- `what`: A string describing the **CONTENT** or action of the requirement (e.g., "go to the restroom"). **注意：“what”应专注于具体行动或事件描述（如“去洗手间”、“查看食堂”），不包含时机描述。请简化描述，去除冗余的口语化表达（例如“带我”等），使行动描述直接、简洁，并完全避免口语化。**
If the USER INPUT contains no requirements, output an empty list `[]` for `requirements`.
If a requirement in the input only specifies `when` or `what` but not the other, still include that requirement in the list, using an empty string `""` for the missing field.

## REQUIREMENTS
You MUST output ONLY a SINGLE VALID JSON OBJECT that strictly follows the structure described above.
You MUST NOT output anything else besides this JSON object, including any additional text, other JSON structures, or invalid JSON.
You MUST NOT HALLUCINATE any requirement not explicitly mentioned in the USER INPUT.
**特别注意：在输出最终的JSON对象时，请确保使用标准的JSON符号（例如使用双引号“”），避免输出任何HTML实体、编码字符或其他特殊符号形式。**
**此外，在提取需求时，请准确区分时机（when）和事件（what）。确保“when”字段只包含时机描述，“what”字段只包含事件描述，避免混淆。对提取到的描述进行简洁化处理。**
**为了继续削弱最终输出中的口语化表述，确保`when`和`what`字段的描述使用简洁、正式的表达式，完全避免日常口语化词汇和冗余表达。**
**在提取时机（`when`）描述时，如果用户输入中同时包含了模糊的口语化时间词（如“等会儿”、“然后”）和具体的、与事件关联的时间描述（如“拿完药之后”），应优先提取并采用该具体的事件关联时间描述，忽略模糊的口语化表达。**

## Example

### Example 1
Input: 给医生看病前，我想先去趟洗手间。
Output:
{
    "requirements": [
        {
            "when": "给医生看病前",
            "what": "去洗手间"
        }
    ]
}

### Example 2
Input: 拿完药之后，带我去趟洗手间。最后原路返回。
Output:
{
    "requirements": [
        {
            "when": "拿完药之后",
            "what": "去洗手间"
        },
        {
            "when": "最后",
            "what": "原路返回"
        }
    ]
}

### Example 3
Input: 先带我去一趟厕所，等会儿拿完药之后带我去医院的饭堂看看有啥饭吃。
Output:
{
    "requirements": [
        {
            "when": "先",
            "what": "去厕所"
        },
        {
            "when": "拿完药之后",
            "what": "去医院饭堂"
        }
    ]
}
"""


_logit_bias = utils.build_logit_bias(
    get_model_func = get_offline_chat_model,
    string_to_probability = {
    },
    token_eos = -5.0, # 降低模型输出结束符概率，鼓励模型输出更多内容，减少意外截断
    json_block = -5.0 # 降低模型输出非纯净 JSON 格式内容的概率
)


async def collect_requirement_online(input: str) -> RequirementCollectorOutput | None:
    """
    使用在线模型进行需求收集
    Args:
        input (RequirementCollectorInput): 用户对自定义需求的描述
    Returns:
        RequirementCollectorOutput: 用户的需求描述
    """

    agent = Agent(
        name = "Requirement Collector Agent in Hospital Route Planner",
        instructions = requirement_collector_instructions,
        model = get_online_chat_model(),
        model_settings = ModelSettings(
            temperature = 0.7,
            max_tokens = 2048,
        ),
    )

    response = await Runner().run(
        starting_agent = agent,
        input = "Input: {}".format(input),
        max_turns = 2 # idk whether the agent will ask multiple rounds of questions
    )

    response_text = response.final_output

    logger.debug(f"[RC Agent] Raw LLM Response (online):\n{response_text}")

    try:
        output: dict = json.loads(response_text)
        return RequirementCollectorOutput(**output)
    except (json.JSONDecodeError, ValidationError) as e:
        logger.error(f"Failed to parse LLM response: {e}")
        return None


async def collect_requirement_offline(input: str) -> RequirementCollectorOutput | None:
    """
    使用离线模型进行需求收集
    Args:
        input (RequirementCollectorInput): 用户对自定义需求的描述
    Returns:
        RequirementCollectorOutput: 用户的需求描述
    """

    offline_reasoning_model = get_offline_chat_model()

    get_response_func = lambda: offline_reasoning_model.create_chat_completion(
        messages = [
            {"role": "system", "content": requirement_collector_instructions},
            {"role": "user", "content": "Input: {}".format(input)}
        ],
        response_format = {"type": "text"},
        temperature = 0.7,
        max_tokens = 1024,
        logit_bias = _logit_bias()
    )

    response = await asyncio.to_thread(get_response_func)
    response_text = str(response["choices"][0]["message"]["content"])

    logger.debug(f"[RC Agent] Raw LLM Response (offline):\n{response_text}")

    try:
        output: dict = json.loads(response_text)
        return RequirementCollectorOutput(**output)
    except (json.JSONDecodeError, ValidationError) as e:
        logger.error(f"Failed to parse LLM response: {e}")
        return None


__all__ = [
    "collect_requirement_online",
    "collect_requirement_offline"
]
