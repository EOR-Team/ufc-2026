# clinic_selector.py
# 诊室选择智能体 - 根据结构化症状数据选择合适的诊室

import json
import asyncio
from agents import Agent, ModelSettings, Runner
from pydantic import BaseModel, Field, ValidationError

from src import logger, utils
from src.smart_triager.typedef import ClinicSelectionOutput
from src.llm.online import get_online_chat_model
from src.llm.offline import get_offline_chat_model
from src.map.tools import clinic_id_to_name_and_description


# ============================================================================
# 动态诊室列表生成函数
# ============================================================================

def generate_dynamic_clinic_list() -> str:
    """生成动态诊室列表文本"""
    if not clinic_id_to_name_and_description:
        # 回退机制：使用默认诊室列表
        default_clinics = {
            "surgery_clinic": "外科诊室 - 处理需手术或操作的外伤、感染、肿瘤等体表及内部疾病",
            "emergency_clinic": "急诊室 - 24小时开放，专门用于抢救与处理突发、危重的伤病员",
            "internal_clinic": "内科诊室 - 通过问诊、查体及非手术方式诊疗人体内部各系统疾病",
            "pediatric_clinic": "儿科诊室 - 专门为14周岁以下儿童及青少年提供疾病诊疗"
        }
        clinic_list = []
        for clinic_id, description in default_clinics.items():
            clinic_list.append(f"- {clinic_id}: {description}")
        return "\n".join(clinic_list)
    
    clinic_list = []
    for clinic_id, info in clinic_id_to_name_and_description.items():
        clinic_list.append(f"- {clinic_id}: {info['name']} - {info['description']}")
    
    return "\n".join(clinic_list)


# ============================================================================
# 系统提示词 (7层结构)
# ============================================================================

# 生成动态诊室列表
_dynamic_clinic_list = generate_dynamic_clinic_list()

clinic_selector_instructions = """## Background
你是一个医院分诊系统中的诊室选择专家。你的任务是根据患者的结构化症状数据，选择最合适的诊室进行就诊。

## Role
你是诊室选择专家，专门负责根据症状的严重程度、持续时间、受影响部位等信息，将患者分配到正确的诊室。

## Input
你会收到一个包含以下信息的结构化症状数据：
1. body_parts: 受影响的身体部位
2. duration: 症状持续时间
3. severity: 症状严重程度
4. description: 症状详细描述
5. other_relevant_information: 其他相关信息列表

## Output
你需要输出一个JSON对象，包含一个字段：
- clinic_selection: 选择的诊室ID

## Available Clinics
以下是医院中可用的诊室列表：
$_dynamic_clinic_list$

## Decision Criteria
请严格按照以下标准选择诊室：

### 急诊诊室 (emergency_clinic)
- 严重外伤、大出血、休克
- 急性腹痛、胸痛、呼吸困难
- 意识丧失、抽搐、高热惊厥
- 中毒、严重过敏反应
- 任何需要立即抢救的危急情况

### 外科诊室 (surgery_clinic)
- 需要手术或操作的外伤
- 感染、脓肿、肿瘤等体表疾病
- 骨折、脱臼、撕裂伤
- 需要缝合、引流、切除的病症
- 术前评估与术后复查

### 内科诊室 (internal_clinic)
- 心脑血管疾病（高血压、冠心病等）
- 呼吸系统疾病（咳嗽、哮喘、肺炎等）
- 消化系统疾病（胃炎、溃疡、肝炎等）
- 内分泌疾病（糖尿病、甲状腺疾病等）
- 肾脏疾病、风湿免疫疾病
- 通过药物和非手术方式治疗的内部疾病
- **轻微或不明确的症状**（当无法确定具体科室时）

### 儿科诊室 (pediatric_clinic)
- 14周岁以下儿童及青少年的疾病
- 儿童生长发育问题
- 儿童特有的传染病
- 需要儿童专用剂量和环境的治疗

## Important Rules
1. **必须选择一个诊室**：无论症状多么轻微或不明确，都必须从上述诊室中选择一个
2. **绝对优先顺序**：
   - 第一步：检查是否是儿童（14岁以下）→ 如果是，选择儿科诊室（pediatric_clinic）
   - 第二步：检查是否是急诊情况 → 如果是，选择急诊诊室（emergency_clinic）
   - 第三步：根据具体症状选择外科或内科诊室
3. **儿童绝对优先**：如果患者是儿童（14岁以下），无论症状如何，都必须优先考虑儿科诊室。只有在儿科诊室不适用的情况下才考虑其他诊室。
4. **内科作为默认**：对于轻微、不明确或无法分类的症状，选择内科诊室
5. **只输出诊室ID**：不要输出任何解释或额外信息

## Example

输入:
{
  "body_parts": "头部",
  "duration": "2小时",
  "severity": "严重",
  "description": "头部受到重击，意识模糊，呕吐",
  "other_relevant_information": ["交通事故", "有出血"]
}

输出:
{
  "clinic_selection": "emergency_clinic"
}

输入:
{
  "body_parts": "手臂",
  "duration": "3天",
  "severity": "中度",
  "description": "手臂骨折，有明显畸形",
  "other_relevant_information": ["摔倒受伤"]
}

输出:
{
  "clinic_selection": "surgery_clinic"
}

输入:
{
  "body_parts": "胸部",
  "duration": "1周",
  "severity": "轻度",
  "description": "咳嗽、咳痰，轻微发热",
  "other_relevant_information": ["无吸烟史"]
}

输出:
{
  "clinic_selection": "internal_clinic"
}

输入:
{
  "body_parts": "全身",
  "duration": "2天",
  "severity": "轻度",
  "description": "5岁儿童发烧，食欲不振",
  "other_relevant_information": ["年龄5岁"]
}

输出:
{
  "clinic_selection": "pediatric_clinic"
}

输入:
{
  "body_parts": "手臂",
  "duration": "1天",
  "severity": "中度",
  "description": "3岁儿童手臂擦伤，有轻微出血",
  "other_relevant_information": ["年龄3岁", "玩耍时摔倒"]
}

输出:
{
  "clinic_selection": "pediatric_clinic"
}

输入:
{
  "body_parts": "不确定",
  "duration": "几天",
  "severity": "轻微",
  "description": "感觉不舒服，但说不清楚具体哪里不舒服",
  "other_relevant_information": []
}

输出:
{
  "clinic_selection": "internal_clinic"
}
""".replace("$_dynamic_clinic_list$", _dynamic_clinic_list)

# ============================================================================
# Logit Bias 配置
# ============================================================================

from src.llm.offline import get_offline_chat_model

def get_logit_bias_config() -> dict:
    """根据动态诊室列表生成 logit_bias 配置"""
    # 获取动态诊室列表
    clinic_ids = list(clinic_id_to_name_and_description.keys()) if clinic_id_to_name_and_description else []
    
    # 如果没有诊室列表，使用默认配置
    if not clinic_ids:
        return {
            "emergency_clinic": 1.5,  # 最高优先级
            "surgery_clinic": 1.3,
            "internal_clinic": 1.0,   # 默认/最低优先级
            "pediatric_clinic": 1.6   # 提高儿科优先级
        }
    
    # 设置优先级
    bias_config = {}
    for clinic_id in clinic_ids:
        if clinic_id == "emergency_clinic":
            bias_config[clinic_id] = 1.5  # 最高优先级
        elif clinic_id == "pediatric_clinic":
            bias_config[clinic_id] = 1.6  # 提高儿科优先级，仅次于急诊
        elif clinic_id == "surgery_clinic":
            bias_config[clinic_id] = 1.3
        elif clinic_id == "internal_clinic":
            bias_config[clinic_id] = 1.0  # 默认/最低优先级
        else:
            bias_config[clinic_id] = 1.2  # 其他诊室中等优先级
    
    return bias_config

_logit_bias = utils.build_logit_bias(
    get_model_func = get_offline_chat_model,
    string_to_probability = get_logit_bias_config(),
    token_eos = -5.0, # 降低模型输出结束符概率，鼓励模型输出更多内容，减少意外截断
)

# ============================================================================
# API 函数 - 在线模型
# ============================================================================

async def select_clinic_online(conditions: ClinicSelectionOutput) -> ClinicSelectionOutput | None:
    """
    使用在线模型选择诊室
    
    Args:
        conditions: ClinicSelectionOutput 对象，包含所有症状信息
    
    Returns:
        ClinicSelectionOutput: 诊室选择结果
        None: 如果选择失败或发生错误，则返回None
    """
    
    # 创建Agent
    agent = Agent(
        name = "Clinic Selection Agent in Hospital Route Planner",
        instructions = clinic_selector_instructions,
        model = get_online_chat_model(),
        model_settings = ModelSettings(
            temperature = 0.6,
            max_tokens = 1024,
        ),
    )
    
    # 运行Agent
    response = await Runner().run(
        starting_agent = agent,
        input = json.dumps(conditions.dict(), ensure_ascii=False, indent=4),
        max_turns = 1 # idk whether the agent will ask multiple rounds of questions
    )
    
    response_text = response.final_output
    
    # 详细日志：输出原始响应用于调试
    logger.debug(f"[CS Agent] Raw LLM Response (online):\n{response_text}")
    
    # 解析响应
    try:
        output: dict = json.loads(response_text)
        result = ClinicSelectionOutput(**output)
        
        # 验证输出是否在诊室列表中
        valid_clinics = list(clinic_id_to_name_and_description.keys()) if clinic_id_to_name_and_description else []
        if valid_clinics and result.clinic_selection not in valid_clinics:
            logger.warning(f"模型输出不在诊室列表中: {result.clinic_selection}，有效列表: {valid_clinics}")
            # 回退到内科诊室
            result.clinic_selection = "internal_clinic"
        
        return result
    except (json.JSONDecodeError, ValidationError) as e:
        logger.error(f"Failed to parse clinic selector output: {e}")
        # 如果解析失败，返回空
        return None

# ============================================================================
# API 函数 - 离线模型
# ============================================================================

async def select_clinic_offline(
    body_parts: str,
    duration: str,
    severity: str,
    description: str,
    other_relevant_information: list[str],
    temperature: float = 0.1,
    max_tokens: int = 100
) -> ClinicSelectionOutput | None:
    """ 
    使用离线模型选择诊室
    
    Args:
        body_parts: 受影响的身体部位
        duration: 症状持续时间
        severity: 症状严重程度
        description: 症状详细描述
        other_relevant_information: 其他相关信息列表
        temperature: 温度参数
        max_tokens: 最大token数
    
    Returns:
        ClinicSelectionOutput: 诊室选择结果
    """
    
    # 构建输入数据
    input_data = {
        "body_parts": body_parts,
        "duration": duration,
        "severity": severity,
        "description": description,
        "other_relevant_information": other_relevant_information
    }
    
    offline_chat_model = get_offline_chat_model()
    
    get_response_func = lambda: offline_chat_model.create_chat_completion(
        messages = [
            {"role": "system", "content": clinic_selector_instructions},
            {"role": "user", "content": json.dumps(input_data, ensure_ascii=False)}
        ],
        response_format = {"type": "text"},
        temperature = temperature,
        max_tokens = max_tokens,
        logit_bias = _logit_bias()
    )
    
    response = await asyncio.to_thread(get_response_func) 
    response_text = str(response["choices"][0]["message"]["content"]) # this type can be ignored
    
    # 详细日志：输出原始响应用于调试
    logger.debug(f"[CS Agent] Raw LLM Response (offline):\n{response_text}")
    
    # 解析响应
    try:
        output: dict = json.loads(response_text)
        result = ClinicSelectionOutput(**output)
        
        # 验证输出是否在诊室列表中
        valid_clinics = list(clinic_id_to_name_and_description.keys()) if clinic_id_to_name_and_description else []
        if valid_clinics and result.clinic_selection not in valid_clinics:
            logger.warning(f"模型输出不在诊室列表中: {result.clinic_selection}，有效列表: {valid_clinics}")
            # 回退到内科诊室
            result.clinic_selection = "internal_clinic"
        
        return result
    except (json.JSONDecodeError, ValidationError) as e:
        logger.error(f"Failed to parse clinic selector output: {e}")
        # 如果解析失败，返回空
        return None


# ============================================================================
# 导出
# ============================================================================

__all__ = [
    "select_clinic_online",
    "select_clinic_offline",
    "ClinicSelectionOutput",
    "generate_dynamic_clinic_list"
]