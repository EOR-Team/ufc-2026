"""
backend/src/medical/agent.py
医疗智能 Agent：根据诊断结果生成病因与疗养建议（面向患者、通俗易懂）
提供在线/离线接口（离线为简单模版回退）
"""

from typing import Optional
from src.llm.online.client import get_online_client
from src.config import general
import json
import asyncio


def _build_prompt(diagnosis_text: str, patient_info: Optional[dict] = None, matched_records: Optional[list[dict]] = None) -> str:
    """构建给 LLM 的详细 prompt，要求生成通俗易懂、面向患者的病因和疗养建议。"""
    prompt = """
你是临床助手，任务是将医生的诊断结果转换为面向患者、通俗易懂的文字，包含：

- 简短结论（1-2句），指出诊断的核心是什么；
- 可能的病因（2-4点），用普通话描述，避免医学专业术语或在术语后加括号说明；
- 简单的疗养与护理建议（4-8点），包含日常生活、饮食、休息、是否需要复诊或用药指引；
- 若有潜在严重症状（需要立即就医）请明确列出并用粗体或开头标注“立即就医：”；
- 语言风格：友好、安抚、鼓励；长度不宜超过 400 字；
- 输出格式：JSON 对象，包含字段 `summary`（结论）、`possible_causes`（数组）、`care_advice`（数组）、`urgent_signs`（数组，若无可空数组）。

请根据下列信息生成结果：
注意：输出要尽量个性化，如果提供了 `patient_info`（例如年龄、既往史）或 `matched_records`（患者历史病历片段），请据此调整建议：
- 在护理建议中注明针对已有疾病/用药的注意事项（不要开具体处方剂量）；
- 在随访建议中给出大致时间范围（例如“3-7天复诊或若症状加重立刻就医”）；
- 在生活方式建议中给出具体可执行动作（例如“每天睡眠保证7-8小时”，“避免剧烈运动直到症状缓解”）；
- 在每条建议后可选提供一句简短的理由（为什么这样做有帮助）。
"""

    prompt += f"\n诊断结果文本：\n{diagnosis_text}\n"

    if patient_info:
        prompt += "\n患者信息（可选）：\n" + json.dumps(patient_info, ensure_ascii=False) + "\n"

    if matched_records:
        # 提供部分历史病历片段供模型参考，但限制长度以防超长
        brief_records = matched_records if len(json.dumps(matched_records, ensure_ascii=False)) < 2000 else matched_records[-5:]
        prompt += "\n匹配到的历史病历片段（可选，用于个性化建议）：\n" + json.dumps(brief_records, ensure_ascii=False) + "\n"

    prompt += "\n请严格返回合法的 JSON（不要输出额外说明文本）。"

    return prompt


def generate_patient_advice(diagnosis_text: str, patient_info: Optional[dict] = None, online_model: bool = True, matched_records: Optional[list[dict]] = None) -> dict:
    """主接口：同步接口，内部对在线模型调用做阻塞/线程切换处理。
    - online_model=True: 使用 DeepSeek/OpenAI 风格在线模型
    - online_model=False: 使用简单模版回退
    返回解析后的 dict 或包含 error 字段的 dict
    """
    if online_model:
        try:
            client = get_online_client()
            # 使用简单的 chat completion 调用
            prompt = _build_prompt(diagnosis_text, patient_info, matched_records)
            # 以同步方式调用（外层 router 会在线程池中调用此函数）
            response = asyncio.run(
                client.chat.completions.create(
                    model=general.ONLINE_CHAT_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2,
                    max_tokens=800,
                )
            )

            # 提取文本内容
            assistant = response.choices[0].message
            content = assistant.content or ""

            # 尝试 parse JSON
            try:
                parsed = json.loads(content)
                return {"success": True, "data": parsed}
            except Exception:
                # 如果返回不是 JSON，则尝试从文本中抽取最后一个 JSON 对象
                last_brace = content.rfind("{")
                if last_brace != -1:
                    maybe = content[last_brace:]
                    try:
                        parsed = json.loads(maybe)
                        return {"success": True, "data": parsed}
                    except Exception:
                        pass

                return {"success": False, "error": "无法解析模型返回内容为 JSON", "raw": content}

        except Exception as e:
            return {"success": False, "error": str(e)}

    # 离线或回退实现：基于模板返回更个性化的建议（使用 patient_info 和 matched_records）
    summary = diagnosis_text.split("。")[0] if diagnosis_text else "未提供诊断结果"
    possible_causes = ["常见原因：病毒或细菌感染，过敏反应，环境刺激等。请在门诊由医生进一步鉴别。"]

    # 个性化护理建议，尽量给出具体可执行项与简短理由
    care_advice = []
    if patient_info and isinstance(patient_info, dict):
        age = patient_info.get("age") or patient_info.get("年龄")
        if age and isinstance(age, int) and age >= 65:
            care_advice.append({"advice": "老年人建议更密切观察体温与呼吸情况，避免脱水与电解质紊乱。", "reason": "老年人免疫力较弱并发症风险更高"})

    care_advice.extend([
        {"advice": "保证充足休息，卧床或减少外出直至症状明显好转。", "reason": "促进免疫恢复，减少传播"},
        {"advice": "保持室内空气流通，避免烟雾与刺激性气体。", "reason": "减少对气道的刺激，缓解咳嗽"},
        {"advice": "多饮水、清淡饮食，避免咖啡因与酒精。", "reason": "帮助稀释痰液与维持体液平衡"},
        {"advice": "按医生建议使用对症药物（如退热、止咳剂），不要自行组合处方药。", "reason": "避免药物相互作用与副作用"},
    ])

    # 如果历史病历提示有慢性病或长期用药，添加注意事项
    if matched_records:
        care_advice.append({"advice": "根据既往病历，注意与既往用药的相互作用并向主治医师说明最近用药史。", "reason": "防止不良药物相互作用"})

    urgent_signs = ["呼吸困难", "持续高热不退（>38.5°C，多日）", "胸痛或意识改变"]

    follow_up = ["若48-72小时症状无改善请复诊","若出现急性呼吸困难或高热请立即就医"]

    suggested_questions = [
        "我的症状可能的病因是什么？需要做哪些检查？",
        "我是否需要使用抗生素或其他处方药？何时应开始用药？",
        "需要何时复诊或做进一步检查？"
    ]

    return {
        "success": True,
        "data": {
            "summary": summary,
            "possible_causes": possible_causes,
            "care_advice": care_advice,
            "urgent_signs": urgent_signs,
            "follow_up": follow_up,
            "suggested_questions_for_doctor": suggested_questions,
        },
    }


__all__ = ["generate_patient_advice"]
