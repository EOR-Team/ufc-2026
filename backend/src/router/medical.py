"""
router/medical.py
医疗建议功能路由
"""

from typing import Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from src.medical.agent import get_medical_response


medical_router = APIRouter(prefix="/medical")


class MedicalSuggestionRequest(BaseModel):
    """医疗建议请求体"""
    
    symptoms: str = Field(..., description="用户最近的症状")
    diagnosis: Optional[str] = Field(default=None, description="医生给予用户的诊断结果（可选）")
    online_model: bool = Field(default=False, description="是否使用在线模型（默认离线模式）")


@medical_router.get("/suggest")
async def get_medical_suggestion_api(
    symptoms: str,
    diagnosis: Optional[str] = None,
    online_model: bool = False
):
    """
    根据症状和诊断结果生成个性化的医疗建议
    
    Args:
        symptoms: 用户最近的症状
        diagnosis: 医生给予用户的诊断结果
        online_model: 是否使用在线模型（默认使用离线模式以优化性能）
    
    Returns:
        JSON格式的响应：{"success": true, "data": {"response": "个性化回复", "scenario": "场景类型", "requires_doctor_consultation": false}}
    """
    
    try:
        response = await get_medical_response(symptoms, diagnosis, online_model)
        
        if response:
            return JSONResponse(
                content={
                    "success": True,
                    "data": response.model_dump()
                },
                status_code=200,
                media_type="application/json"
            )
        else:
            return JSONResponse(
                content={
                    "success": False,
                    "error": "无法生成医疗建议"
                },
                status_code=500,
                media_type="application/json"
            )
            
    except Exception as e:
        return JSONResponse(
            content={
                "success": False,
                "error": f"内部错误: {str(e)}"
            },
            status_code=500,
            media_type="application/json"
        )