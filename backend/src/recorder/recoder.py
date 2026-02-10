from IntegratedSystem.integrated_system import IntegratedSystem
from agents import function_tool,Agent,ModelSettings

system = IntegratedSystem()  # 获取系统实例
@function_tool
def enroll_new_patient(name, timeout=30.0):
    """
    录入新患者（人脸录入 + 创建病历）
    :param name: 患者姓名
    :param timeout: 超时时间
    :return: {"name": name, "id": id} 或 None
    """
    return system.enroll_new_patient(name, timeout)

@function_tool
def recognize_patient(timeout=30.0):
    """
    通过人脸识别来识别患者
    :param timeout: 超时时间
    :return: {"name": name, "id": id} 或 None
    """
    return system.recognize_patient(timeout)

@function_tool
def add_medical_record(patient_id, medical_record):
    """
    为患者添加病历
    :param patient_id: 患者ID
    :param medical_record: 病历内容
    :return: bool
    """    
    return system.add_medical_record(patient_id, medical_record)

@function_tool
def get_patient_info(patient_id):
    """
    获取患者完整信息
    :param patient_id: 患者ID
    :return: 患者信息字典或None
    """
    return system.get_patient_info(patient_id)

@function_tool
def delete_patient(patient_id):
    """
    删除患者（同时删除人脸和病历）
    :param patient_id: 患者ID
    :return: bool
    """
    return system.delete_patient(patient_id)

_prompt_markdown ="""
# 基于人脸识别的智能病历系统
"""

recoder_agent = Agent(
    name="RecorderAgent",
    instructions=_prompt_markdown,
    tools=[enroll_new_patient, recognize_patient, add_medical_record, get_patient_info, delete_patient],
    model=None,  # 这里不指定模型，实际使用时会注入在线模型
    model_settings=ModelSettings(
        temperature=0,
    )
)