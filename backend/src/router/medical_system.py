"""
router/medical_system.py
集成人脸识别系统和病历管理系统的接口，提供统一的患者信息管理功能。
"""

from fastapi import APIRouter, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.IntegratedSystem.integrated_system import AsyncIntegratedSystem
from src.config.general import BACKEND_ROOT_DIR
from src import logger


medical_system_router = APIRouter(prefix="/medical")
system = AsyncIntegratedSystem()

FACE_IMG_PATH = BACKEND_ROOT_DIR / "assets" / "face" / "face.png"


class EnrollRequest(BaseModel):
    name: str

class RecordRequest(BaseModel):
    patient_id: int
    medical_record: str


@medical_system_router.post("/upload_face_img")
async def upload_face_img(file: UploadFile):
    FACE_IMG_PATH.parent.mkdir(parents=True, exist_ok=True)
    FACE_IMG_PATH.write_bytes(await file.read())
    logger.info("[upload_face_img] saved")
    return JSONResponse({"success": True}, status_code=200)


@medical_system_router.post("/enroll")
async def enroll(request: EnrollRequest):
    result = await system.enroll_new_patient_async(request.name)
    if result:
        return JSONResponse({"success": True, "data": result}, status_code=200)
    return JSONResponse({"success": False, "error": "Enroll failed."}, status_code=500)


@medical_system_router.post("/recognize")
async def recognize():
    result = await system.recognize_patient_async()
    if result:
        return JSONResponse({"success": True, "data": result}, status_code=200)
    return JSONResponse({"success": False, "error": "No match found."}, status_code=404)


@medical_system_router.post("/record")
async def add_record(request: RecordRequest):
    ok = await system.add_medical_record_async(request.patient_id, request.medical_record)
    if ok:
        return JSONResponse({"success": True}, status_code=200)
    return JSONResponse({"success": False, "error": "Patient not found."}, status_code=404)


@medical_system_router.get("/patient/{patient_id}")
async def get_patient(patient_id: int):
    info = await system.get_patient_info_async(patient_id)
    if info:
        return JSONResponse({"success": True, "data": info}, status_code=200)
    return JSONResponse({"success": False, "error": "Patient not found."}, status_code=404)


@medical_system_router.delete("/patient/{patient_id}")
async def delete_patient(patient_id: int):
    ok = await system.delete_patient_async(patient_id)
    if ok:
        return JSONResponse({"success": True}, status_code=200)
    return JSONResponse({"success": False, "error": "Patient not found."}, status_code=404)
