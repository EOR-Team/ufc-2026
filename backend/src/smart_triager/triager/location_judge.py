"""
smart_triager/triager/location_judge.py
根据用户输入的身体状况判断应该分诊到的诊室地点。
"""

import json
import asyncio

from agents import Agent, ModelSettings, Runner

from src import logger
from src.map.typedef import *
from src.llm.online import get_online_reasoning_model
from src.llm.offline import get_offline_reasoning_model
from src.smart_triager.typedef import *


location_judge_instructions = """
## Background
You are now working in a SMART TRIAGE and ROUTING system which is designed for a **CHINESE** HOSTPITAL ENVIRONMENT.
Your system's entire purpose is to plan routes for users based on their specific needs and constraints.

## Role
You are a Department Judge Agent whose job is to DETERMINE the most APPROPRIATE department for a user to go to SEE A DOCTOR BASED ON their described physical condition, feeling, and symptoms.

## Task
Your job is to ANALYZE the STRUCTURED INFORMATION about the user's physical condition, feelings, and symptoms, and DETERMINE which department EXISTING IN THE HOSPITAL they should be directed to IN ORDER TO RECEIVE THE MOST APPROPRIATE CARE from doctors.
You MUST ensure that you have made a decision that is BASED ON THE STRUCTURED INFORMATION PROVIDED and it MUST be the BEST CHOICE according to provided information.

## Input
You will receive 2 pieces of information:
1. `current_summary`: A concise summary of the user's current PHYSICAL CONDITION, FEELINGS, and SYMPTOMS. This summary is analyzed and structured information that is extracted from the user's original input.
Here is the structure of `current_summary`: <|current_summary_schema|>
2. `location_id_to_info`: A dictionary mapping location IDs to their corresponding information. Each location's information includes:
- `id`: The unique identifier for the location, which is WHAT YOU SHOULD OUTPUT as your decision's RESULT.
- `name`: The name of the location, which is for your REFERENCE ONLY to help you understand what the location is. However, it is NOT the field you should output.
- `description`: The descriptions of what the location is for, which is for you REFERENCE ONLY to help you UNDERSTAND what the location is for. However, it is NOT the field you should output.
ATTENTION: Some of which may be non-department locations such as pharmacy, laboratory, etc. You should JUDGE IN DEPARTMENTS ONLY, and you SHOULD NOT JUDGE NON-DEPARTMENT LOCATIONS.
You should JUDGE THE MOST APPROPRIATE DEPARTMENT. If there are multiple departments that are all APPROPRIATE, you should JUDGE THE MOST APPROPRIATE ONE among them. You should NOT JUDGE A DEPARTMENT THAT IS LESS APPROPRIATE THAN ANOTHER DEPARTMENT.

## Output
Your output MUST be a STRING that is the `id` of the department that you JUDGE to be the MOST APPROPRIATE for the user to go to SEE A DOCTOR BASED on the `current_summary` and the information of each department in `location_id_to_info`.

## REQUIREMENTS
1. Your decision MUST be BASED ON THE STRUCTURED INFORMATION PROVIDED in `current_summary` and the information of each department in `location_id_to_info`. You MUST NOT make a decision that is NOT SUPPORTED BY THE PROVIDED INFORMATION.
2. You MUST JUDGE the MOST APPROPRIATE DEPARTMENT for the user's condition. You MUST NOT JUDGE a location that is LESS APPROPRIATE than another location based on the provided information.
3. You MUST ONLY OUTPUT THE `id` of the DEPARTMENT that you JUDGE to be the MOST APPROPRIATE. 
4. You MUST NOT OUTPUT ANY OTHER FIELD, ANY OTHER XML TAGS and ANY OTHER TEXT.

## Example

### Example 1
Input:
{
    "current_summary": {
        "body_parts": "脚踝",
        "duration": "两三天",
        "other_relevant_information": "两三天前扭伤过一次，但是很快就好了。现在又开始不舒服了",
        "severity": "走路时会刺痛"
    },
    "location_id_to_info": {
        "orthopedic": {
            "id": "orthopedic",
            "name": "骨科",
            "description": "处理骨骼、关节、肌肉、韧带等运动系统相关问题的科室"
        },
        "surgery_clinic": {
            "id": "surgery_clinic",
            "name": "外科门诊",
            "description": "处理需手术或操作的外伤、感染、肿瘤等体表及内部疾病，进行术前评估与术后复查。"
        },
        "phramecy": {
            "id": "pharmacy",
            "name": "药房",
            "description": "提供处方药和非处方药的购买服务，供患者购买医生开具的药物。"
        },

    }
}
Analysis:
1. The user's current summary indicates that he/she has an issue with the ANKLE that exists from a previous injury for 3 days, which is a part of the MUSCULOSKELETAL SYSTEM.
2. There is an ORTHOPEDIC department that is RESPONSIBLE for handling issues related to the MUSCULOSKELETAL SYSTEM, which is the most appropriate department for the user to go to SEE A DOCTOR.
Output:
orthopedic
""".replace("<|current_summary_schema|>", str(CurrentSummary.model_json_schema()))


async def judge_location_online(info: LocationJudgeInput) -> LocationJudgeOutput:
    """
    使用在线模型进行诊室判断
    Args:
        info (LocationJudgeInput): 包含当前患者明确症状的总结和地图中所有诊室的信息字典。
    Returns:
        LocationJudgeOutput: 诊室的id
    """

    agent = Agent(
        name = "Department Judge Agent in Hospital Route Planner",
        instructions = location_judge_instructions,
        model = get_online_reasoning_model(),
        model_settings = ModelSettings(
            temperature = 0.5,
            max_tokens = 10,
        ),
    )

    response = await Runner().run(
        starting_agent = agent,
        input = "Input: {}".format(info.model_dump_json()),
        max_turns = 2 # idk whether the agent will ask multiple rounds of questions
    )

    response_text
