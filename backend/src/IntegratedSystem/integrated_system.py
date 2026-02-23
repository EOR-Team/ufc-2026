from face_recognition_system import FaceRecognitionSystem
from medical_record_system import MedicalRecordSystem
class IntegratedSystem:
    """集成人脸识别和病历管理的系统"""
    
    def __init__(self):
        self.face_system = FaceRecognitionSystem()
        self.medical_system = MedicalRecordSystem()
    
    def enroll_new_patient(self, name, image_path: str | None = None):
        """
        录入新患者（从静态图片录入人脸并创建病历）
        - 默认使用 `backend/assets/face/face.png`，也可通过 `image_path` 指定图片
        :param name: 患者姓名
        :param image_path: 可选自定义图片路径
        :return: {"name": name, "id": id} 或 None
        """
        # 从图片录入人脸
        result = self.face_system.enroll_face_realtime(name, image_path)
        
        if result:
            # 自动创建病历
            self.medical_system.create_patient(result['name'], result['id'])
            return result
        
        return None
    
    def recognize_patient(self, image_path: str | None = None):
        """
        从静态图片识别患者（默认使用 `backend/assets/face/face.png`）
        :param image_path: 可选自定义图片路径
        :return: {"name": name, "id": id} 或 None
        """
        return self.face_system.recognize_face_realtime(image_path)
    
    def add_medical_record(self, patient_id, medical_record):
        """
        为患者添加病历
        :param patient_id: 患者ID
        :param medical_record: 病历内容
        :return: bool
        """
        return self.medical_system.append_record(patient_id, medical_record)
    
    def get_patient_info(self, patient_id):
        """
        获取患者完整信息
        :param patient_id: 患者ID
        :return: 患者信息字典或None
        """
        return self.medical_system.read(patient_id)
    
    def delete_patient(self, patient_id):
        """
        删除患者（同时删除人脸和病历）
        :param patient_id: 患者ID
        :return: bool
        """
        face_deleted = self.face_system.delete(patient_id)
        medical_deleted = self.medical_system.delete(patient_id)
        return face_deleted and medical_deleted


def main():
    """使用示例"""
    system = IntegratedSystem()
    
    # 录入新患者（使用默认图片 backend/assets/face/face.png）
    result = system.enroll_new_patient("张三")
    print(f"录入结果：{result}")
    
    # 识别患者（使用默认图片 backend/assets/face/face.png）
    result = system.recognize_patient()
    if result:
        print(f"识别到患者：{result['name']}, ID: {result['id']}")
    
    # 添加病历
    system.add_medical_record(1, "2024-02-10: 感冒，开药...")
    
    # 读取患者信息
    info = system.get_patient_info(1)
    print(info)
    
    # 删除患者
    system.delete_patient(1)
    
    print("集成系统已就绪")


if __name__ == "__main__":
    main()