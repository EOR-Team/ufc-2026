"""
router/voice.py
语音相关功能 路由
- 语音转文本 STT
- 文本转语音 TTS
"""

import io

from fastapi import APIRouter, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.responses import FileResponse

import magic
from pydub import AudioSegment

from src.voice_interaction.voice_interaction import VoiceInteraction


voice_router = APIRouter(prefix="/voice")


@voice_router.post("/stt")
@voice_router.post("/stt/")  # 支持尾部斜杠
async def stt(file: bytes = File(...)):
    """
    语音转文本接口
    支持多种音频格式：WebM, WAV
    """
    vi = VoiceInteraction()
    input_wav_path = "./assets/input.wav"

    try:
        # 检测音频格式
        file_type = magic.from_buffer(file[:1024]) if len(file) >= 1024 else magic.from_buffer(file)

        # 记录检测到的格式
        print(f"[STT] 检测到音频格式: {file_type}")

        if 'WAV' in file_type or 'RIFF' in file_type:
            # 直接保存 WAV 文件
            with open(input_wav_path, "wb") as f:
                f.write(file)
            print(f"[STT] 保存 WAV 文件成功，大小: {len(file)} 字节")

        elif 'WebM' in file_type or 'Matroska' in file_type or 'EBML' in file_type:
            try:
                # 转换 WebM 到 WAV (16kHz 单声道)
                audio = AudioSegment.from_file(io.BytesIO(file), format="webm")
                audio = audio.set_frame_rate(16000).set_channels(1)  # 16kHz 单声道
                audio.export(input_wav_path, format="wav")
                print(f"[STT] 转换 WebM 到 WAV 成功，大小: {len(file)} 字节")
            except Exception as conv_error:
                print(f"[STT] WebM转换失败: {conv_error}")
                raise HTTPException(
                    status_code=400,
                    detail=f"WebM音频转换失败，需要ffmpeg支持。请安装ffmpeg或使用其他格式。错误: {conv_error}"
                )

        elif 'MPEG' in file_type or 'MP4' in file_type:
            try:
                # 转换 MP4 到 WAV
                audio = AudioSegment.from_file(io.BytesIO(file), format="mp4")
                audio = audio.set_frame_rate(16000).set_channels(1)
                audio.export(input_wav_path, format="wav")
                print(f"[STT] 转换 MP4 到 WAV 成功，大小: {len(file)} 字节")
            except Exception as conv_error:
                print(f"[STT] MP4转换失败: {conv_error}")
                raise HTTPException(
                    status_code=400,
                    detail=f"MP4音频转换失败，需要ffmpeg支持。错误: {conv_error}"
                )

        elif 'Ogg' in file_type or 'Opus' in file_type:
            try:
                # 转换 OGG/Opus 到 WAV
                audio = AudioSegment.from_file(io.BytesIO(file), format="ogg")
                audio = audio.set_frame_rate(16000).set_channels(1)
                audio.export(input_wav_path, format="wav")
                print(f"[STT] 转换 OGG/Opus 到 WAV 成功，大小: {len(file)} 字节")
            except Exception as conv_error:
                print(f"[STT] OGG/Opus转换失败: {conv_error}")
                raise HTTPException(
                    status_code=400,
                    detail=f"OGG/Opus音频转换失败，需要ffmpeg支持。错误: {conv_error}"
                )

        else:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的音频格式: {file_type}。支持格式: WAV, WebM, MP4, OGG/Opus。请安装ffmpeg以支持非WAV格式。"
            )

        # 调用语音识别
        recognized_text = await vi.stt_async()
        return JSONResponse(content={"text": recognized_text})

    except HTTPException:
        raise
    except Exception as e:
        print(f"[STT] 处理音频文件时发生错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"音频处理失败: {str(e)}"
        )


@voice_router.get("/tts")
async def tts(text: str):
    """
    文本转语音接口
    """

    vi = VoiceInteraction()

    voice_file_path = await vi.tts_async(text)

    with open(voice_file_path, "rb") as f:
        return FileResponse(voice_file_path, media_type="audio/wav", filename="output.wav")