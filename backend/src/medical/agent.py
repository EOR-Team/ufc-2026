"""
backend/src/medical/agent.py
医疗智能 Agent：根据症状和诊断结果生成个性化医疗建议
支持场景识别和模板化回复，优化边缘计算性能
"""

from typing import Optional, Tuple
from pydantic import BaseModel
from src.llm.online.client import get_online_client
from src.config import general
import json
import asyncio
import re


class MedicalResponse(BaseModel):
    """医疗响应数据模型"""
    response: str
    scenario: str
    requires_doctor_consultation: bool = False


def _identify_scenario(symptoms: str, diagnosis: Optional[str] = None) -> Tuple[str, bool]:
    """
    识别场景类型和安全边界检查
    返回：(场景类型, 是否需要医生咨询)
    """
    # 关键词定义
    medication_keywords = ["服药", "用药", "剂量", "一次", "两次", "三次", "吃药", "药量"]
    dangerous_keywords = ["改剂量", "减量", "增量", "停药", "自行调整", "减少用药", "增加用药"]
    
    text = f"{symptoms} {diagnosis or ''}".lower()
    
    # 检查是否需要医生咨询（安全边界）
    requires_doctor = any(keyword in text for keyword in dangerous_keywords)
    
    # 场景识别
    if any(keyword in text for keyword in medication_keywords):
        scenario = "medication_consultation"
    elif "疗养" in text or "恢复" in text or "休养" in text:
        scenario = "recovery_advice"
    elif "症状" in text or "诊断" in text:
        scenario = "symptom_interpretation"
    else:
        scenario = "general_advice"
    
    return scenario, requires_doctor


def _extract_medication_info(text: str) -> dict:
    """提取用药相关信息"""
    info = {}
    
    # 匹配用药频率
    freq_patterns = [
        r"一天\s*(\d+)\s*次",
        r"每日\s*(\d+)\s*次",
        r"(\d+)\s*次\s*每天",
        r"(\d+)\s*次/天"
    ]
    
    for pattern in freq_patterns:
        match = re.search(pattern, text)
        if match:
            info["frequency"] = int(match.group(1))
            break
    
    # 简单药物识别（常见药物关键词）
    med_keywords = ["抗生素", "消炎药", "退烧药", "止痛药", "感冒药", "止咳药"]
    for keyword in med_keywords:
        if keyword in text:
            info["medication"] = keyword
            break
    
    return info


def _generate_template_response(scenario: str, symptoms: str, diagnosis: Optional[str], requires_doctor: bool) -> str:
    """生成模板化回复"""
    
    if requires_doctor:
        return "⚠️ **重要提醒**：关于用药剂量的调整，必须咨询主治医生。自行调整用药剂量可能导致治疗效果不佳或产生不良反应。请务必遵医嘱服药，如有疑问请及时联系医生。"
    
    if scenario == "medication_consultation":
        med_info = _extract_medication_info(f"{symptoms} {diagnosis}")
        
        if med_info["frequency"]:
            return f"""根据您的描述，您提到关于用药频率的问题。

**重要原则**：用药频率是医生根据药物特性、病情严重程度和个体差异精心制定的，不应自行更改。

**建议**：
1. 严格按医嘱服药：一天{med_info["frequency"]}次，保持规律
2. 如有不适或疑问，及时联系医生或药师
3. 不要因为症状减轻而自行减量或停药
4. 完成整个疗程，确保彻底康复

**提醒**：任何用药调整都需医生评估，请勿自行决定。"""
        
        return """关于用药问题，请遵循以下原则：

1. **遵医嘱服药**：严格按照医生开具的处方用药
2. **按时按量**：不要随意更改服药时间和剂量
3. **完成疗程**：即使症状好转，也应完成整个治疗周期
4. **及时沟通**：如有不适或疑问，及时联系医生

用药安全至关重要，请勿自行调整用药方案。"""
    
    elif scenario == "recovery_advice":
        # 根据常见症状提供个性化建议
        advice_parts = []
        
        if any(symptom in symptoms for symptom in ["发烧", "发热", "高热"]):
            advice_parts.append("• **体温管理**：注意监测体温，适当物理降温，避免过度捂汗")
        
        if any(symptom in symptoms for symptom in ["咳嗽", "咳痰", "喉咙痛"]):
            advice_parts.append("• **呼吸道护理**：保持室内空气流通，多喝温水，避免刺激性气体")
        
        if any(symptom in symptoms for symptom in ["腹泻", "腹痛", "消化不良"]):
            advice_parts.append("• **消化道调理**：饮食清淡易消化，注意补充水分和电解质")
        
        if any(symptom in symptoms for symptom in ["头痛", "头晕", "乏力"]):
            advice_parts.append("• **休息恢复**：保证充足睡眠，避免劳累，适当休息")
        
        # 基础建议
        base_advice = [
            "• **充分休息**：保证每天7-8小时睡眠，避免过度劳累",
            "• **合理饮食**：营养均衡，多摄入蛋白质和维生素",
            "• **适度活动**：根据体力状况进行轻度活动，促进恢复",
            "• **遵医嘱**：按时服药，定期复查",
            "• **观察症状**：注意症状变化，如有加重及时就医"
        ]
        
        all_advice = advice_parts + base_advice
        
        return f"""根据您的诊断情况，以下是个性化的疗养建议：

{chr(10).join(all_advice)}

**重要提醒**：
1. 每个人的恢复情况不同，请根据自身感受调整
2. 如出现新症状或原有症状加重，请及时就医
3. 保持良好心态，积极面对康复过程

祝您早日康复！"""
    
    elif scenario == "symptom_interpretation":
        diagnosis_text = diagnosis or "暂无诊断信息"
        return f"""根据您的症状描述和诊断结果：

**症状分析**：{symptoms}

**诊断说明**：{diagnosis_text}

**理解建议**：
1. 诊断结果反映了您当前的健康状况
2. 症状是身体发出的信号，需要认真对待
3. 严格按照医生的治疗方案执行
4. 如有不理解的地方，可以再次咨询医生

**注意事项**：
• 不要自行诊断或使用偏方
• 定期复查，跟踪恢复进展
• 保持与医生的良好沟通"""
    
    else:  # general_advice
        diagnosis_text = diagnosis or "暂无诊断信息"
        return f"""感谢您的咨询。根据您提供的信息：

**症状**：{symptoms}
**诊断**：{diagnosis_text}

**一般性建议**：
1. 严格遵循医生的治疗方案
2. 注意休息，避免劳累
3. 保持均衡饮食，多喝水
4. 观察身体反应，及时反馈给医生
5. 如有紧急情况，立即就医

**重要原则**：健康问题请以专业医生意见为准，本建议仅供参考。"""


async def get_medical_response_online(symptoms: str, diagnosis: Optional[str] = None) -> Optional[MedicalResponse]:
    """使用在线模型获取医疗回复"""
    try:
        client = get_online_client()
        
        diagnosis_line = f"医生诊断：{diagnosis}" if diagnosis else "医生诊断：暂无"
        prompt = f"""你是专业的医疗助手，请根据患者的症状和诊断结果，提供个性化、简洁易读的医疗建议。

患者症状：{symptoms}
{diagnosis_line}

要求：
1. 回复要严谨准确，避免给出可能有害的建议
2. 语言简洁明了，用通俗易懂的中文
3. 如果涉及用药调整，必须强调"咨询医生"的重要性
4. 回复长度控制在200字以内
5. 直接给出建议，不要使用JSON格式

请生成回复："""
        
        response = await client.chat.completions.create(
            model=general.ONLINE_CHAT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,  # 降低随机性，提高准确性
            max_tokens=400,
        )

        content = response.choices[0].message.content or ""
        
        # 识别场景
        scenario, requires_doctor = _identify_scenario(symptoms, diagnosis)
        
        return MedicalResponse(
            response=content.strip(),
            scenario=scenario,
            requires_doctor_consultation=requires_doctor
        )
            
    except Exception:
        return None


def get_medical_response_offline(symptoms: str, diagnosis: Optional[str] = None) -> MedicalResponse:
    """离线模式：基于模板生成回复"""
    scenario, requires_doctor = _identify_scenario(symptoms, diagnosis)
    response = _generate_template_response(scenario, symptoms, diagnosis, requires_doctor)
    
    return MedicalResponse(
        response=response,
        scenario=scenario,
        requires_doctor_consultation=requires_doctor
    )


async def get_medical_response(symptoms: str, diagnosis: Optional[str] = None, online_model: bool = False) -> Optional[MedicalResponse]:
    """主接口：获取医疗回复（默认使用离线模式以优化性能）"""
    if online_model:
        return await get_medical_response_online(symptoms, diagnosis)
    else:
        return get_medical_response_offline(symptoms, diagnosis)


__all__ = [
    "MedicalResponse",
    "get_medical_response",
    "get_medical_response_online",
    "get_medical_response_offline"
]