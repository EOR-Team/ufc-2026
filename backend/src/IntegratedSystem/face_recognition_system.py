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
    
    def enroll_face_realtime(self, name, timeout=30.0):
        """
        实时录入人脸（当存在多个人脸时拒绝录入）
        :param name: 人脸标签
        :param timeout: 超时时间（秒）
        :return: {"name": name, "id": id} 或 None
        """
        video_capture = cv2.VideoCapture(0)
        start_time = time.time()
        
        print(f"开始录入 '{name}'，请面向摄像头...")
        print("检测到单个人脸时按空格键录入，按q退出")
        
        while True:
            # 检查超时
            if time.time() - start_time > timeout:
                print("录入超时")
                video_capture.release()
                cv2.destroyAllWindows()
                return None
            
            ret, frame = video_capture.read()
            if not ret:
                break
            
            # 检测人脸
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            face_count = len(face_locations)
            
            # 显示提示信息
            if face_count == 0:
                status = "未检测到人脸"
                color = (0, 0, 255)
            elif face_count == 1:
                status = "按空格键录入"
                color = (0, 255, 0)
                # 绘制人脸框
                top, right, bottom, left = face_locations[0]
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            else:
                status = f"检测到{face_count}个人脸，请保持单人"
                color = (0, 165, 255)
            
            cv2.putText(frame, status, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            cv2.imshow('Face Enrollment', frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            # 按q退出
            if key == ord('q'):
                video_capture.release()
                cv2.destroyAllWindows()
                return None
            
            # 按空格键录入（仅当只有一个人脸时）
            if key == ord(' ') and face_count == 1:
                face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
                if len(face_encodings) > 0:
                    patient_id = self._get_next_id()
                    self._append_data(face_encodings[0], name, patient_id)
                    result = {"name": name, "id": patient_id}
                    print(f"成功录入：{name}，ID：{patient_id}")
                    video_capture.release()
                    cv2.destroyAllWindows()
                    return result
        
        video_capture.release()
        cv2.destroyAllWindows()
        return None
    
    def recognize_face_realtime(self, timeout=30.0):
        """
        实时识别人脸并返回标签
        :param timeout: 超时时间（秒）
        :return: {"name": name, "id": id} 或 None
        """
        video_capture = cv2.VideoCapture(0)
        start_time = time.time()
        
        print("开始识别，识别到人脸后按空格键确认，按q退出")
        
        while True:
            # 检查超时
            if time.time() - start_time > timeout:
                print("识别超时")
                video_capture.release()
                cv2.destroyAllWindows()
                return None
            
            ret, frame = video_capture.read()
            if not ret:
                break
            
            # 检测和识别人脸
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            
            detected_result = None
            
            for encoding, location in zip(face_encodings, face_locations):
                name_info = None
                
                # 与已知人脸比对
                if len(self.known_encodings) > 0:
                    matches = face_recognition.compare_faces(
                        self.known_encodings, encoding, tolerance=0.6
                    )
                    if True in matches:
                        face_distances = face_recognition.face_distance(
                            self.known_encodings, encoding
                        )
                        best_match_index = face_distances.argmin()
                        if matches[best_match_index]:
                            name_info = self.known_names[best_match_index]
                            detected_result = name_info
                
                # 绘制人脸框和标签
                top, right, bottom, left = location
                color = (0, 255, 0) if name_info else (0, 0, 255)
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                
                label = name_info['name'] if name_info else "未知"
                cv2.putText(frame, label, (left, top - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)
            
            # 显示提示
            hint = "按空格键确认识别结果" if detected_result else "未识别到已录入人脸"
            cv2.putText(frame, hint, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imshow('Face Recognition', frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            # 按q退出
            if key == ord('q'):
                video_capture.release()
                cv2.destroyAllWindows()
                return None
            
            # 按空格键确认返回
            if key == ord(' ') and detected_result:
                print(f"识别到：{detected_result['name']}，ID：{detected_result['id']}")
                video_capture.release()
                cv2.destroyAllWindows()
                return detected_result
        
        video_capture.release()
        cv2.destroyAllWindows()
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
