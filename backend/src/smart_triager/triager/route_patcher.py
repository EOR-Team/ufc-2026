"""
smart_triager/triager/route_patcher.py
路径修改器
"""

import json
import asyncio
from agents import Agent, ModelSettings, Runner

from src import logger, utils
from src.llm.online import get_online_reasoning_model
from src.llm.offline import get_offline_chat_model
from src.smart_triager.typedef import *
from src.map import main_node_id_to_name_and_description


def generate_route(specific_clinic_id: str) -> list[LocationLink]:
    """
    根据先前生成的特定诊室ID，生成一条新路线作为后续修改的基础

    Args:
        specific_clinic_id (str): 先前生成的特定诊室ID
    Returns:
        list[LocationLink]: 生成的新路线
    """

    route_ids = [
        "entrance",
        "registration_center",
        specific_clinic_id,
        "payment_center",
        "pharmacy",
        "quit"
    ]

    return generate_route_by_ids(*route_ids)


def _transform_input_to_text(
    destination_clinic_id: str,
    requirement_summary: list[Requirement],
    origin_route: list[LocationLink]
) -> str:
    """
    将输入的结构化数据转换为文本描述，供模型理解和生成

    Args:
        destination_clinic_id (str): 用户的目的地诊室ID
        requirement_summary (list[Requirement]): 用户的需求摘要列表
        origin_route (list[LocationLink]): 原路线列表

    Returns:
        str: 转换后的文本描述
    """

    input_obj = {
        "destination_clinic_id": destination_clinic_id,
        "requirement_summary": [r.model_dump() for r in requirement_summary],
        "origin_route": [link.model_dump() for link in origin_route]
    }

    return json.dumps(input_obj, ensure_ascii=False, indent=2)


route_patcher_instructions = """
## Background
You are now working in a SMART TRIAGE and ROUTING system designed for a **CHINESE** HOSPITAL ENVIRONMENT. The system's ultimate goal is to plan routes for users based on their specific needs and constraints.

## Role
You are a Route Patcher Agent whose job is to MAKE MODIFICATIONS to the original route in order to SUIT the user's CONDITIONS and REQUIREMENTS.
You are given: 1. An original route which is bind to the general surgery_clinic; 2. a string ID which represents the user's destinational clinic to visit; 3. descriptions about the user's current conditions and requirements.
You need to make modification to the original route, by INSERTING and DELETING some locations in the original route, to make the final route more SUITABLE for the user's conditions and requirements.
Your tasks are as follows:
1. Understand the user's requirements based on the provided descriptions.
2. Make modifications on the destinational clinic in the original route, to make the final route more SUITABLE for the user's conditions and requirements.
3. Make modifications to the original route ACCORDING TO the user's CUSTOM REQUIREMENTS by INSERTING and DELETING some locations, to make the final route more SUITABLE for the user's conditions and requirements.

## Input
You will receive an JSON object consisting of 4 kinds of information:
- `destination_clinic_id`: The ID of the clinic that the user is going to visit, which is a string. You can refer to the `locations` field to get the name and description of this clinic.
    This field maybe empty, which means that the DEFAULT destinational clinic is the surgery_clinic, and you won't need to make modifications to the original route for this field.
- `requirement_summary`: The user's custom requirements, which is a LIST of requirements structured as:
    - `when`: A string describing the **TIMING** or sequence of the requirement (e.g., "before seeing the doctor", "after getting medicine")
    - `what`: A string describing the **CONTENT** or action of the requirement (e.g., "go to the restroom").
- `locations`: A DICT containing ALL USING LOCATIONS which you need to SELECT to make modifications to the original route.
    - `<location_id>`: The ID of a location, which is the KEY in the `locations` dict. The value is a DICT containing 2 fields:
        - `name`: The name of the location, which is a string. helpful for you to understand the location and make decisions.
        - `description`: A detailed description of the location, which is a string. helpful for you to understand the location and make decisions.
- `origin_route`: A LIST of location IDs representing the original route. You MUST make modifications based on this original route.
    - `this`: The ID of a location in the original route. You can refer to the `locations` field to get the name and description of this location.
    - `next`: The ID of the next location in the original route. You can refer to the `locations` field to get the name and description of this location.

## Locations Information
Here is the information of all locations you can use to make modifications to the original route:
$locations_mark$

## Output
Your output MUST be a SINGLE VALID PURE JSON object containing a `patches` field which is a PATCH LIST that describes how you will make changes to the original route.
The structure of A SINGLE PATCH is as follows:
- `type`: The description of each patch. ONLY CHOOSE BETWEEN "insert" and "delete".
- `previous`: The ID of the location after which you will make the modification. (For "insert" type, it means the location after which you will insert a new location. For "delete" type, it means the location after which you will delete the next location.)
- `this`: The ID of the location you want to insert or delete. (For "insert" type, it means the location you want to insert. For "delete" type, it means the location you want to delete, which should be the next location after `previous` in the original route.)
- `next`: The ID of the location before which you will make the modification. (For "insert" type, it means the location before which you will insert a new location. For "delete" type, it means the location before which you will delete the previous location.)

ALL FIELDS IN THE OUTPUT ARE REQUIRED, and you MUST output ALL FIELDS for EACH PATCH.

If there is no modification needed, output an empty list `[]` for `patches`.
If there are some modifications needed, output a list of patches in the `patches` field. You can output as many patches as you need, but please try to minimize the number of patches and make sure each patch is necessary and helpful for making the final route more suitable for the user's conditions and requirements.

## Criteria for Modifications
1. If the user mention words like "现在" that refers to the current time, you should UNDERSTAND it that the user is at the ENTRANCE of the hospital now. It means that if the user has a requirement with "when" containing "现在", you should make modifications to the original route at the very beginning, which is right after the ENTRANCE for this requirement FOR SURE. For other requirements, follow criteria below to make modifications.
2. For requirements with "when" containing "给医生看病前", you should make modifications to the original route before a CERTAIN CLINIC LOCATION (e.g., surgery_clinic, internal_clinic) in the original route, which means that the `next` field of the patch should be this clinic location. You can choose to insert some locations before this clinic location, or delete some locations immediately before this clinic location, to satisfy the user's requirements.
3. For requirements with "when" containing "拿完药之后", you should make modifications to the original route after the PHARMACY, which means that the `previous` field of the patch should be the PHARMACY. You can choose to insert some locations immediately after the PHARMACY, or delete some locations immediately after the PHARMACY, to satisfy the user's requirements.
4. For requirements with "when" containing "最后", you should make modifications to the original route at the very end, which is right before the QUIT for this requirement FOR SURE.
5. For requirements with other "when" description, you can make modifications to the original route at any place you think is suitable, but please make sure the modifications are reasonable and can effectively make the final route more suitable for the user's conditions and requirements.
6. If the destination clinic ID is provided and it is different from the clinic in the original route, you MUST make modifications to change the clinic in the original route to this destination clinic. You can choose to insert the destination clinic before the original clinic and delete the original clinic, or directly replace the original clinic with the destination clinic, or any other modification method that can effectively change the clinic in the original route to the destination clinic.
7. If the destination clinic ID is provided and it is the same as the clinic in the original route, you don't need to make modifications for this field, but you can still make other modifications based on the user's requirements.

ATTENTION:
When parsing your patches, the `delete` type patches will be applied to the original route FIRST, then the `insert` type patches will be applied, which means that the modifications described in `delete` type patches will be executed before the modifications described in `insert` type patches.

## REQUIREMENTS
You MUST output ONLY a SINGLE VALID JSON OBJECT that strictly follows the structure described above.
You MUST NOT output anything else besides this JSON object, including any additional text, other JSON structures, or invalid JSON.
You MUST NOT HALLUCINATE any patch that is not explicitly supported by the user's conditions and requirements.
**特别注意：在输出最终的JSON对象时，请确保使用标准的JSON符号（例如使用双引号“”），避免输出任何HTML实体、编码字符或其他特殊符号形式。**
**此外，在设计修改方案时，请确保每个修改都是合理且必要的，能够有效地使最终路线更适合用户的条件和需求。请避免任何不必要的修改，以保持路线的简洁和效率。**
**在设计修改方案时，请优先考虑那些能够同时满足多个需求的修改，以最大化修改的效果和效率。**

## Example

### Example 1
Input:
{
    "destination_clinic_id": "surgery_clinic", 
    "requirement_summary": [
        {
            "when": "给医生看病前",
            "what": "去洗手间"
        }
    ],
    "origin_route": $origin_route_mark$
}
Output:
{
    "patches": [
        {
            "type": "insert",
            "previous": "registration_center",
            "this": "toliet",
            "next": "surgery_clinic"
        }
    ]
}

### Example 2
Input:
{
    "destination_clinic_id": "internal_clinic",
    "requirement_summary": [
        {
            "when": "现在",
            "what": "去洗手间"
        }
    ],
    "origin_route": $origin_route_mark$
}
Output:
{
    "patches": [
        {
            "type": "insert",
            "previous": "entrance",
            "this": "toliet",
            "next": "registration_center"
        },
        {
            "type": "delete",
            "previous": "registration_center",
            "this": "surgery_clinic",
            "next": "payment_center"
        },
        {
            "type": "insert",
            "previous": "registration_center",
            "this": "internal_clinic",
            "next": "payment_center"
        }
    ]
}

### Example 3
Input:
{
    "destination_clinic_id": "internal_clinic",
    "requirement_summary": [
        {
            "when": "拿完药之后",
            "what": "去洗手间"
        }
    ],
    "origin_route": $origin_route_mark$
}
Output:
{
    "patches": [
        {
            "type": "insert",
            "previous": "pharmacy",
            "this": "toliet",
            "next": "quit"
        },
        {
            "type": "delete",
            "previous": "registration_center",
            "this": "surgery_clinic",
            "next": "payment_center"
        },
        {
            "type": "insert",
            "previous": "registration_center",
            "this": "internal_clinic",
            "next": "payment_center"
        }
    ]
}

""" .replace("$locations_mark$", json.dumps(main_node_id_to_name_and_description, ensure_ascii=False, indent=4)) \


_logit_bias = utils.build_logit_bias(
    get_model_func = get_offline_chat_model,
    string_to_probability = {
    },
    token_eos = -5.0, # 降低模型输出结束符概率，鼓励模型输出更多内容，减少意外截断
    json_block = -5.0 # 降低模型输出非纯净 JSON 格式内容的概率
)


async def patch_route_online(
    destination_clinic_id: str,
    requirement_summary: list[Requirement],
    origin_route: list[LocationLink] = generate_route("surgery_clinic")
) -> RoutePatcherOutput | None:
    """
    根据用户的目的地诊室ID和需求摘要，生成对原路线的修改方案

    Args:
        destination_clinic_id (str): 用户的目的地诊室ID
        requirement_summary (list[Requirement]): 用户的需求摘要列表
        origin_route (list[LocationLink]): 原路线列表，默认为基于surgery_clinic生成的路线

    Returns:
        RoutePatcherOutput: 路线修改方案列表
    """

    agent = Agent(
        name = "Route Patcher Agent in Hospital Route Planner",
        instructions = route_patcher_instructions.replace(
            "$origin_route_mark$",
            json.dumps([link.model_dump() for link in generate_route(destination_clinic_id)], ensure_ascii=False, indent=4)
        ),
        model = get_online_reasoning_model(),
        model_settings = ModelSettings(
            temperature = 0.6,
            max_tokens = 4096,
        ),
    )

    response = await Runner().run(
        starting_agent = agent,
        input = "Input: {}".format( _transform_input_to_text(destination_clinic_id, requirement_summary, origin_route) ),
        max_turns = 1 # idk whether the agent will ask multiple rounds of questions
    )

    response_text = response.final_output

    logger.debug(f"[RP Agent] Raw LLM Response (online):\n{response_text}")

    try:
        output: dict = json.loads(response_text)
        return RoutePatcherOutput(**output)
    except (json.JSONDecodeError, ValidationError) as e:
        logger.error(f"Failed to parse LLM response: {e}")
        return None


async def patch_route_offline(
    destination_clinic_id: str,
    requirement_summary: list[Requirement],
    origin_route: list[LocationLink]
) -> RoutePatcherOutput | None:
    """
    根据用户的目的地诊室ID和需求摘要，生成对原路线的修改方案

    Args:
        destination_clinic_id (str): 用户的目的地诊室ID
        requirement_summary (list[Requirement]): 用户的需求摘要列表
        origin_route (list[LocationLink]): 原路线列表，默认为基于surgery_clinic生成的路线

    Returns:
        RoutePatcherOutput: 路线修改方案列表
    """

    model = get_offline_chat_model()

    get_response_func = lambda: model.create_chat_completion(
        messages = [
            {"role": "system", "content": route_patcher_instructions.replace(
                "$origin_route_mark$",
                json.dumps([link.model_dump() for link in generate_route(destination_clinic_id)], ensure_ascii=False, indent=4)
            )},
            {"role": "user", "content": "Input: {}".format( _transform_input_to_text(destination_clinic_id, requirement_summary, origin_route) )}
        ],
        response_format = {"type": "text"},
        temperature = 0.6,
        max_tokens = 1024,
        logit_bias = _logit_bias()
    )

    response = await asyncio.to_thread(get_response_func)
    response_text = str(response["choices"][0]["message"]["content"])

    logger.debug(f"[RP Agent] Raw LLM Response (offline):\n{response_text}")

    try:
        output: dict = json.loads(response_text)
        return RoutePatcherOutput(**output)
    except (json.JSONDecodeError, ValidationError) as e:
        logger.error(f"Failed to parse LLM response: {e}")
        return None


__all__ = [
    "patch_route_online",
    "patch_route_offline",
    "generate_route"
]

