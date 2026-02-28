"""
简单人脸识别系统
功能：实时录入和识别人脸
"""

import os
os.environ["QT_QPA_PLATFORM"] = "xcb"
os.environ["QT_QPA_FONTDIR"] = "/usr/share/fonts"

import cv2
import face_recognition
import pickle
import time
from pathlib import Path

from src.config.general import BACKEND_ROOT_DIR


class FaceRecognitionSystem:

    def __init__(self, data_file="face_data.pkl"):
        """初始化人脸识别系统"""
        self.data_file = data_file
        self.known_encodings = []
        self.known_names = []
        self._load_data()
    

    def _load_data(self):
        """加载已录入的人脸数据"""
        if Path(self.data_file).exists():
            with open(self.data_file, 'rb') as f:
                data = pickle.load(f)
                self.known_encodings = data.get('encodings', [])
                self.known_names = data.get('names', [])
    

    def _append_data(self, encoding, name, patient_id):
        """追加新人脸数据到文件末尾"""
        # 重新加载以获取最新数据
        self._load_data()
        # 追加新数据
        self.known_encodings.append(encoding)
        self.known_names.append({"name": name, "id": patient_id})
        # 保存到文件
        with open(self.data_file, 'wb') as f:
            pickle.dump({
                'encodings': self.known_encodings,
                'names': self.known_names
            }, f)
    

    def _get_next_id(self):
        """获取下一个可用的ID"""
        if not self.known_names:
            return 1
        # 提取所有已有的ID
        existing_ids = [item['id'] for item in self.known_names]
        return max(existing_ids) + 1
    

    def enroll_face_realtime(self, name, image_path: str | None = None):
        """
        从静态图片录入人脸：读取后端仓库中的图片进行识别并录入。
        - 默认图片位置：backend/assets/face/face.png
        - 若图片中检测到多于1张人脸则拒绝录入
        :param name: 人脸标签
        :param image_path: 可选自定义图片路径（文件路径字符串）
        :return: {"name": name, "id": id} 或 None
        """
        # 计算默认图片路径（backend/assets/face/face.png）
        default_image = BACKEND_ROOT_DIR / "assets" / "face" / "face.png"
        img_path = Path(image_path) if image_path else default_image

        if not img_path.exists():
            print(f"人脸录入失败：图片未找到 {img_path}")
            return None

        # 读取图片并检测人脸
        frame = cv2.imread(str(img_path))
        if frame is None:
            print(f"无法读取图片：{img_path}")
            return None

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_count = len(face_locations)

        if face_count == 0:
            print("人脸录入失败：未检测到人脸")
            return None
        if face_count > 1:
            print(f"人脸录入失败：检测到{face_count}个人脸，要求单人照片")
            return None

        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        if not face_encodings:
            print("人脸录入失败：无法计算人脸特征")
            return None

        patient_id = self._get_next_id():
        self._append_data(face_encodings[0], name, patient_id)
        result = {"name": name, "id": patient_id}
        print(f"成功录入：{name}，ID：{patient_id}")
        return result
    

    def recognize_face_realtime(self, image_path: str | None = None):
        """
        从静态图片识别人脸并返回标签：读取 backend/assets/face/face.png（默认）
        - 若图片中检测到多张人脸，将返回第一个匹配到的已录入人脸
        :param image_path: 可选自定义图片路径
        :return: {"name": name, "id": id} 或 None
        """
        default_image = BACKEND_ROOT_DIR / "assets" / "face" / "face.png"
        img_path = Path(image_path) if image_path else default_image

        if not img_path.exists():
            print(f"人脸识别失败：图片未找到 {img_path}")
            return None

        frame = cv2.imread(str(img_path))
        if frame is None:
            print(f"无法读取图片：{img_path}")
            return None

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for encoding in face_encodings:
            if len(self.known_encodings) > 0:
                matches = face_recognition.compare_faces(self.known_encodings, encoding, tolerance=0.6)
                if True in matches:
                    face_distances = face_recognition.face_distance(self.known_encodings, encoding)
                    best_match_index = face_distances.argmin()
                    if matches[best_match_index]:
                        name_info = self.known_names[best_match_index]
                        print(f"识别到：{name_info['name']}，ID：{name_info['id']}")
                        return name_info

        print("未识别到已录入人脸")
        return None
    

    def delete(self, patient_id):
        """
        删除指定ID的人脸数据
        :param patient_id: 要删除的患者ID
        :return: True表示删除成功，False表示未找到该ID
        """
        # 重新加载最新数据
        self._load_data()
        
        # 查找匹配ID的索引
        index_to_remove = None
        for i, name_info in enumerate(self.known_names):
            if name_info['id'] == patient_id:
                index_to_remove = i
                break
        
        if index_to_remove is None:
            print(f"未找到ID：{patient_id}")
            return False
        
        # 删除数据
        del self.known_encodings[index_to_remove]
        del self.known_names[index_to_remove]
        
        # 保存更新后的数据
        with open(self.data_file, 'wb') as f:
            pickle.dump({
                'encodings': self.known_encodings,
                'names': self.known_names
            }, f)
        
        print(f"已删除ID为 {patient_id} 的数据")
        return True
    

def main():
    """示例使用"""
    face_system = FaceRecognitionSystem()
    
    # 录入人脸
    # result = face_system.enroll_face_realtime("张三", timeout=30.0)
    # print(f"录入结果：{result}")  # {"name": "张三", "id": 1} 或 None
    
    # 识别人脸
    # result = face_system.recognize_face_realtime(timeout=30.0)
    # print(f"识别结果：{result}")  # {"name": "张三", "id": 1} 或 None
    
    # 删除人脸
    # success = face_system.delete(1)
    # print(f"删除结果：{success}")
    
    print("使用说明：")
    print("1. 录入：result = system.enroll_face_realtime(name, timeout=30.0)")
    print("2. 识别：result = system.recognize_face_realtime(timeout=30.0)")
    print("3. 删除：success = system.delete(id)")


if __name__ == "__main__":
    main()
