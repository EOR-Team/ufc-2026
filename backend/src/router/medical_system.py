"""
router/medical_system.py
病历与医疗 agent 路由
"""

import io
import json
from typing import Optional

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse

from pydantic import BaseModel, Field

from src.config import general
from src import logger
from src.recorder import recoder
from src.medical import agent as medical_agent

import asyncio

medical_system_router = APIRouter(prefix="/medical")


class UploadFaceRequest(BaseModel):
    """上传人脸图片（接受 bytes 上传时使用 File）"""
    # placeholder for swagger when not using multipart
    pass


class EnrollRequest(BaseModel):
    name: str = Field(..., description="患者姓名")
    image_path: Optional[str] = Field(None, description="可选图片路径，默认后台人脸图片")


class RecognizeRequest(BaseModel):
    image_path: Optional[str] = Field(None, description="可选图片路径，默认后台人脸图片")


class RecordRequest(BaseModel):
    patient_id: int = Field(..., description="患者ID")
    medical_record: str = Field(..., description="病历内容")


class GenerateAdviceRequest(BaseModel):
    patient_id: Optional[int] = Field(None, description="患者ID，可选")
    diagnosis_text: str = Field(..., description="诊断结果或摘要")
    online_model: bool = Field(True, description="是否使用在线模型生成建议")
    matched_records: Optional[list[dict]] = Field(None, description="可选：从检索到的历史病历注入，用于个性化建议")


@medical_system_router.post("/upload_face_img/")
async def upload_face_img(file: UploadFile = File(...)):
    """接收上传的图片字节并写入到默认人脸图片路径"""
    try:
        data = await file.read()
        face_path = general.BACKEND_ROOT_DIR / "assets" / "face" / "face.png"
        face_path.parent.mkdir(parents=True, exist_ok=True)
        with open(face_path, "wb") as f:
            f.write(data)

        return JSONResponse(content={"success": True, "path": str(face_path)})
    except Exception as e:
        logger.error(f"[medical.upload_face_img] {e}")
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)


@medical_system_router.post("/enroll/")
async def enroll(request: EnrollRequest):
    """录入新患者（调用 recoder.enroll_new_patient）"""
    try:
        # 调用同步函数到线程池
        result = await asyncio.to_thread(recoder.enroll_new_patient, request.name, request.image_path)
        if result:
            return JSONResponse(content={"success": True, "data": result})
        else:
            return JSONResponse(content={"success": False, "error": "Enroll failed"}, status_code=500)
    except Exception as e:
        logger.error(f"[medical.enroll] {e}")
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)


@medical_system_router.post("/recognize/")
async def recognize(request: RecognizeRequest):
    """识别患者（调用 recoder.recognize_patient）"""
    try:
        result = await asyncio.to_thread(recoder.recognize_patient, request.image_path)
        if result:
            # 返回患者信息
            return JSONResponse(content={"success": True, "data": result})
        else:
            return JSONResponse(content={"success": False, "error": "No match"}, status_code=404)
    except Exception as e:
        logger.error(f"[medical.recognize] {e}")
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)


@medical_system_router.post("/record/")
async def add_record(request: RecordRequest):
    """为患者追加病历（调用 recoder.add_medical_record）"""
    try:
        ok = await asyncio.to_thread(recoder.add_medical_record, request.patient_id, request.medical_record)
        return JSONResponse(content={"success": ok})
    except Exception as e:
        logger.error(f"[medical.add_record] {e}")
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)


@medical_system_router.get("/patient/{patient_id}")
async def get_patient(patient_id: int):
    """获取患者信息"""
    try:
        info = await asyncio.to_thread(recoder.get_patient_info, patient_id)
        if info:
            return JSONResponse(content={"success": True, "data": info})
        else:
            return JSONResponse(content={"success": False, "error": "Not found"}, status_code=404)
    except Exception as e:
        logger.error(f"[medical.get_patient] {e}")
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)


@medical_system_router.delete("/patient/{patient_id}")
async def delete_patient(patient_id: int):
    """删除患者"""
    try:
        ok = await asyncio.to_thread(recoder.delete_patient, patient_id)
        return JSONResponse(content={"success": ok})
    except Exception as e:
        logger.error(f"[medical.delete_patient] {e}")
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)


@medical_system_router.post("/search_records/")
async def search_records(query: dict):
    """根据前端发送的诊断事件信息查找匹配病历（简单关键词匹配实现）
    请求体示例: {"query": "咳嗽 发热"} 或者 {"patient_id": 1, "query": "咳嗽"}
    """
    try:
        q = query.get("query") if isinstance(query, dict) else None
        patient_id = query.get("patient_id") if isinstance(query, dict) else None

        # 读取所有或指定患者的病历
        matches = []
        if patient_id is not None:
            info = await asyncio.to_thread(recoder.get_patient_info, int(patient_id))
            if not info:
                return JSONResponse(content={"success": False, "error": "patient not found"}, status_code=404)
            records = info.get("medical_records", [])
            for r in records:
                if not q or q in r:
                    matches.append({"patient_id": patient_id, "record": r})
        else:
            # 遍历所有患者文件（读取 recoder.system.medical_system 数据文件）
            # 由于 recoder 没有提供列出所有患者接口，尝试读取文件
            try:
                data_file = recoder.system.medical_system.data_file
                with open(data_file, "r", encoding="utf-8") as f:
                    patients = json.load(f)
                for p in patients:
                    for r in p.get("medical_records", []):
                        if not q or q in r:
                            matches.append({"patient_id": p.get("id"), "record": r})
            except Exception:
                # 退回空结果
                matches = []

        return JSONResponse(content={"success": True, "data": matches})

    except Exception as e:
        logger.error(f"[medical.search_records] {e}")
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)


@medical_system_router.post("/generate_advice/")
async def generate_advice(request: GenerateAdviceRequest):
    """调用医疗 agent，根据诊断结果生成病因与疗养建议（面向患者，通俗易懂）"""
    try:
        # 获取患者信息（可选）
        patient_info = None
        if request.patient_id is not None:
            patient_info = await asyncio.to_thread(recoder.get_patient_info, int(request.patient_id))

        # 调用 medical agent（传入可选的 matched_records 用于个性化）
        result = await asyncio.to_thread(
            medical_agent.generate_patient_advice,
            request.diagnosis_text,
            patient_info,
            request.online_model,
            request.matched_records,
        )

        return JSONResponse(content={"success": True, "data": result})

    except Exception as e:
        logger.error(f"[medical.generate_advice] {e}")
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)
