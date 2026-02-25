"""
router/voice.py
语音相关功能 路由
- 语音转文本 STT
- 文本转语音 TTS
"""


from fastapi import APIRouter, File
from fastapi.responses import JSONResponse
from fastapi.responses import FileResponse

from src.voice_interaction.voice_interaction import VoiceInteraction


voice_router = APIRouter(prefix="/voice")


@voice_router.post("/stt")
async def stt(file: bytes = File(...)):
    """
    语音转文本接口
    """

    vi = VoiceInteraction()

    # 保存上传的音频文件
    input_wav_path = "./assets/input.wav"
    with open(input_wav_path, "wb") as f:
        f.write(file)

    return JSONResponse( content = {"text": await vi.stt_async()} )


@voice_router.get("/tts")
async def tts(text: str):
    """
    文本转语音接口
    """

    vi = VoiceInteraction()

    voice_file_path = await vi.tts_async(text)

    with open(voice_file_path, "rb") as f:
        return FileResponse(voice_file_path, media_type="audio/wav", filename="output.wav")