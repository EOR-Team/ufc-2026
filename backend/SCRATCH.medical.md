# IntegratedSystem 模块阅读总结

## 1. 模块用途与功能

`src/IntegratedSystem/` 是一个**患者信息管理模块**，将人脸识别和病历管理两个子系统整合为统一接口，供 FastAPI 路由层调用。

核心功能：
- **录入患者**：从图片中提取人脸特征并创建病历档案
- **识别患者**：通过图片匹配已录入人脸，返回患者身份
- **管理病历**：追加/读取病历记录
- **删除患者**：同时清除人脸数据和病历

## 2. 模块设计与使用方式

### 类层次

```
IntegratedSystem              ← 同步门面类，组合两个子系统
  └── AsyncIntegratedSystem   ← 异步包装，所有方法用 asyncio.to_thread() 包装
        ↑ 路由层应使用此类

FaceRecognitionSystem         ← 人脸编码存储（二进制序列化文件）
MedicalRecordSystem           ← 病历存储（JSON 文件）
```

### 数据存储

| 文件 | 格式 | 内容 |
|------|------|------|
| `face_data.pkl` | 二进制 | `{encodings: [...], names: [{name, id}, ...]}` |
| `medical_records.json` | JSON | `[{name, id, medical_records: [str, ...]}, ...]` |

两个文件均使用**相对路径**，实际创建在 uvicorn 启动时的 CWD（即 `backend/`）。

### API 接口（AsyncIntegratedSystem）

```python
system = AsyncIntegratedSystem()

# 录入新患者（图片默认 backend/assets/face/face.png）
result = await system.enroll_new_patient_async(name, image_path=None)
# 返回: {"name": str, "id": int} 或 None

# 识别患者
result = await system.recognize_patient_async(image_path=None)
# 返回: {"name": str, "id": int} 或 None

# 追加病历
ok = await system.add_medical_record_async(patient_id: int, medical_record: str)
# 返回: bool

# 读取患者信息
info = await system.get_patient_info_async(patient_id: int)
# 返回: {"name": str, "id": int, "medical_records": [str, ...]} 或 None

# 删除患者（同时删除人脸+病历）
ok = await system.delete_patient_async(patient_id: int)
# 返回: bool
```

### 路由层使用模式

- 在模块级别实例化一个 `AsyncIntegratedSystem` 单例（参考 `recorder/recoder.py` 的 `system = IntegratedSystem()`）
- 所有端点调用 `_async` 后缀方法
- 图片上传流程：前端先将图片写入 `backend/assets/face/face.png`，再调用识别/录入接口

## 3. 需要注意的问题

### Bug 1：语法错误（阻断性）
`face_recognition_system.py:101`：
```python
patient_id = self._get_next_id():  # ← 末尾多了冒号，SyntaxError
```
**必须修复**，否则整个模块无法导入。

### Bug 2：包导入路径错误（阻断性）
`integrated_system.py:8-9`：
```python
from face_recognition_system import FaceRecognitionSystem  # ← 裸导入，包内无效
from medical_record_system import MedicalRecordSystem
```
应改为：
```python
from src.IntegratedSystem.face_recognition_system import FaceRecognitionSystem
from src.IntegratedSystem.medical_record_system import MedicalRecordSystem
```

### 设计限制
- 图片路径默认为固定的 `face.png`，同一时刻只能处理一张图片（无并发安全）
- `patient_id` 是自增整数，无 UUID
- 病历内容是纯字符串，无时间戳结构

---

## 4. 路由实现计划（`router/medical_system.py`）

`medical_system_router` 已挂载在 `/api/medical/`（见 `router/__init__.py:11`）。

默认人脸图片路径：`BACKEND_ROOT_DIR / "assets" / "face" / "face.png"`（来自 `config/general.py`）

### 端点列表

| 方法 | 路径 | 对应方法 | 说明 |
|------|------|----------|------|
| POST | `/upload_face_img` | — | 接收图片字节，写入默认路径 |
| POST | `/enroll` | `enroll_new_patient_async(name)` | 录入新患者 |
| POST | `/recognize` | `recognize_patient_async()` | 识别患者 |
| POST | `/record` | `add_medical_record_async(patient_id, record)` | 追加病历 |
| GET  | `/patient/{patient_id}` | `get_patient_info_async(patient_id)` | 读取患者信息 |
| DELETE | `/patient/{patient_id}` | `delete_patient_async(patient_id)` | 删除患者 |

所有端点均使用模块级单例 `system = AsyncIntegratedSystem()`。
