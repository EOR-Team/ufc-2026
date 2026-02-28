# Medical System API

Base URL: `/api/medical`

---

## 工作原理

系统由两个子系统组成：

- **FaceRecognitionSystem**：使用 `face_recognition` 库对人脸编码进行比对，人脸数据持久化存储在本地文件中。
- **MedicalRecordSystem**：将患者信息（姓名、ID、病历列表）以 JSON 格式持久化存储在 `medical_records.json` 中。

两者通过 `AsyncIntegratedSystem`（单例）统一管理，所有操作均通过 `asyncio.to_thread` 异步化，不阻塞主线程。

**人脸图片约定**：所有人脸操作（录入/识别）默认读取 `backend/assets/face/face.png`。前端需在调用录入或识别接口前，先通过 `/upload_face_img` 上传当前帧图片。

---

## 接口列表

### 1. 上传人脸图片

```
POST /api/medical/upload_face_img
```

**用途**：将前端采集的人脸图片上传并覆盖到服务器的默认路径，供后续录入/识别接口使用。

**请求**：`multipart/form-data`

| 字段 | 类型 | 说明 |
|------|------|------|
| `file` | File | 人脸图片文件（jpg/png） |

**响应**：
```json
{ "success": true }
```

---

### 2. 录入新患者

```
POST /api/medical/enroll
```

**用途**：读取当前 `face.png`，提取人脸编码并存储，同时自动创建对应病历档案。

**请求体**：
```json
{ "name": "张三" }
```

**响应（成功）**：
```json
{
  "success": true,
  "data": { "name": "张三", "id": 1 }
}
```

**响应（失败，如图片中无人脸）**：
```json
{ "success": false, "error": "Enroll failed." }  // HTTP 500
```

> `id` 由系统自动分配，前端需保存此 ID 用于后续操作。

---

### 3. 识别患者

```
POST /api/medical/recognize
```

**用途**：读取当前 `face.png`，与已录入的所有人脸编码比对，返回匹配的患者信息。

**请求体**：无

**响应（识别成功）**：
```json
{
  "success": true,
  "data": { "name": "张三", "id": 1 }
}
```

**响应（无匹配）**：
```json
{ "success": false, "error": "No match found." }  // HTTP 404
```

---

### 4. 添加病历记录

```
POST /api/medical/record
```

**用途**：向指定患者的病历列表追加一条记录。

**请求体**：
```json
{
  "patient_id": 1,
  "medical_record": "2026-02-28: 发烧38.5°C，开退烧药。"
}
```

**响应（成功）**：
```json
{ "success": true }
```

**响应（患者不存在）**：
```json
{ "success": false, "error": "Patient not found." }  // HTTP 404
```

---

### 5. 获取患者信息

```
GET /api/medical/patient/{patient_id}
```

**用途**：获取患者的完整信息，包括所有历史病历。

**路径参数**：`patient_id`（整数）

**响应（成功）**：
```json
{
  "success": true,
  "data": {
    "name": "张三",
    "id": 1,
    "medical_records": [
      "2026-02-28: 发烧38.5°C，开退烧药。"
    ]
  }
}
```

**响应（患者不存在）**：
```json
{ "success": false, "error": "Patient not found." }  // HTTP 404
```

---

### 6. 删除患者

```
DELETE /api/medical/patient/{patient_id}
```

**用途**：同时删除该患者的人脸编码数据和病历档案，操作不可逆。

**路径参数**：`patient_id`（整数）

**响应（成功）**：
```json
{ "success": true }
```

**响应（患者不存在）**：
```json
{ "success": false, "error": "Patient not found." }  // HTTP 404
```

---

## 典型前端流程

### 录入新患者
1. 采集人脸图片帧
2. `POST /upload_face_img` 上传图片
3. `POST /enroll` 传入姓名，保存返回的 `id`

### 识别并查询病历
1. 采集人脸图片帧
2. `POST /upload_face_img` 上传图片
3. `POST /recognize` 获取 `id`
4. `GET /patient/{id}` 获取完整病历
