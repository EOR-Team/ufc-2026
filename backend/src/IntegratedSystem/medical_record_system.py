"""
病历管理系统
与人脸识别系统集成
"""

import json
from pathlib import Path


class MedicalRecordSystem:
    def __init__(self, data_file="medical_records.json"):
        """初始化病历管理系统"""
        self.data_file = data_file
        self.patients = []
        self._load_data()
    
    def _load_data(self) -> None:
        """加载病历数据"""
        if Path(self.data_file).exists():
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.patients = json.load(f)
    
    def _save_data(self) -> None:
        """保存病历数据"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.patients, f, ensure_ascii=False, indent=2)
    
    def create_patient(self, name: str, patient_id: int) -> bool:
        """
        新建患者（通常在人脸录入后调用）
        :param name: 患者姓名
        :param patient_id: 患者ID
        :return: True表示创建成功
        """
        # 重新加载最新数据
        self._load_data()
        
        # 检查ID是否已存在
        for patient in self.patients:
            if patient['id'] == patient_id:
                print(f"ID {patient_id} 已存在，无法创建")
                return False
        
        # 创建新患者
        new_patient = {
            "name": name,
            "id": patient_id,
            "medical_records": []
        }
        
        self.patients.append(new_patient)
        self._save_data()
        print(f"成功创建患者：{name}，ID：{patient_id}")
        return True
    
    def append_record(self, patient_id: int, medical_record: str) -> bool:
        """
        追加病历
        :param patient_id: 患者ID
        :param medical_record: 病历内容（字符串）
        :return: True表示追加成功，False表示未找到患者
        """
        # 重新加载最新数据
        self._load_data()
        
        # 查找患者
        for patient in self.patients:
            if patient['id'] == patient_id:
                patient['medical_records'].append(medical_record)
                self._save_data()
                print(f"成功为患者 ID {patient_id} 追加病历")
                return True
        
        print(f"未找到ID为 {patient_id} 的患者")
        return False
    
    def read(self, patient_id: int) -> dict | None:
        """
        读取患者信息
        :param patient_id: 患者ID
        :return: 包含name、id、medical_records的字典，未找到则返回None
        """
        # 重新加载最新数据
        self._load_data()
        
        for patient in self.patients:
            if patient['id'] == patient_id:
                return patient
        
        print(f"未找到ID为 {patient_id} 的患者")
        return None
    
    def delete(self, patient_id: int) -> bool:
        """
        删除患者信息
        :param patient_id: 患者ID
        :return: True表示删除成功，False表示未找到
        """
        # 重新加载最新数据
        self._load_data()
        
        # 查找并删除
        for i, patient in enumerate(self.patients):
            if patient['id'] == patient_id:
                del self.patients[i]
                self._save_data()
                print(f"已删除患者 ID {patient_id}")
                return True
        
        print(f"未找到ID为 {patient_id} 的患者")
        return False



