import os
import asyncio
import re
import threading
import wave
from typing import Optional
from src.logger import info, warning, error, debug
import piper
from piper.voice import PiperVoice

class TextToSpeech:
    def __init__(self, path="./assets", model_path: Optional[str] = None):
        """
        初始化Piper TTS引擎

        Args:
            path: 输出音频文件保存目录
            model_path: Piper语音模型文件路径 (.onnx)
                      如果为None，则尝试使用默认中文模型路径
        """
        self.output_path = path
        # Piper默认采样率是22050 Hz
        self.sample_rate = 22050
        os.makedirs(self.output_path, exist_ok=True)

        # 设置模型路径
        if model_path is None:
            # 默认中文语音模型路径 - 使用新下载的模型
            model_path = os.path.join(
                os.path.dirname(__file__),
                "../../model/tts/zh_CN-huayan-medium.onnx"
            )

        self.model_path = model_path
        self._voice: Optional[PiperVoice] = None  # 懒加载

        info(f"Piper TTS initialized. Model path: {self.model_path}")

        # 检查模型文件是否存在
        if not os.path.exists(self.model_path):
            warning(f"Piper model file not found at: {self.model_path}")
            warning("Please download a Chinese Piper model from:")
            warning("https://huggingface.co/rhasspy/piper-voices/tree/main/zh")
            warning("Available models: zh_CN-huayan-medium.onnx, zh_CN-xiao_ya-medium.onnx")

    def _ensure_voice(self) -> PiperVoice:
        """确保Piper语音模型已加载（懒加载）"""
        if self._voice is None:
            if not os.path.exists(self.model_path):
                raise RuntimeError(
                    f"Piper model file not found: {self.model_path}\n"
                    "Please download a Chinese Piper model and place it in the models directory.\n"
                    "You can download from: https://huggingface.co/rhasspy/piper-voices/tree/main/zh"
                )

            info(f"Loading Piper model: {self.model_path}")
            self._voice = PiperVoice.load(self.model_path)
            info(f"Piper model loaded successfully")

        return self._voice

    def generate(self, text, output="output.wav"):
        """
        生成语音文件

        Piper TTS支持中文、英文及混合文本
        保持文本清理以兼容旧代码
        """
        path = os.path.join(self.output_path, output)

        # 清理文本：移除可能引起问题的特殊字符
        # 保留中文、英文、数字和基本标点
        text = re.sub(r'[^\u4e00-\u9fff\w\s.,!?，。！？]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()

        if not text:
            text = "无内容"

        # 加载语音模型
        voice = self._ensure_voice()

        # 生成语音文件
        try:
            info(f"Generating speech for text: {text[:50]}...")

            # 方法1: 使用synthesize()并手动构建WAV文件（基于官方文档）
            info("尝试方法1: 使用synthesize()手动构建WAV...")
            try:
                # 收集音频数据
                audio_data = b""
                sample_rate = None
                sample_width = None
                channels = None

                # 使用synthesize()获取音频块
                for chunk in voice.synthesize(text):
                    # 保存第一块的格式信息
                    if sample_rate is None:
                        # 尝试获取音频格式信息
                        sample_rate = getattr(chunk, 'sample_rate', 22050)
                        sample_width = getattr(chunk, 'sample_width', 2)
                        channels = getattr(chunk, 'channels', 1)
                        info(f"音频格式: {sample_rate}Hz, {sample_width}字节/样本, {channels}声道")

                    # 获取音频数据
                    if hasattr(chunk, 'audio_bytes'):
                        audio_data += chunk.audio_bytes
                    elif hasattr(chunk, 'audio'):
                        audio_data += chunk.audio
                    elif hasattr(chunk, 'audio_int16_bytes'):
                        audio_data += chunk.audio_int16_bytes
                    else:
                        # 尝试直接访问可能的属性
                        warning(f"chunk缺少标准音频数据属性，可用的属性: {[a for a in dir(chunk) if not a.startswith('_')]}")
                        # 回退到原始方法
                        raise RuntimeError("无法从chunk获取音频数据")

                info(f"收集到音频数据: {len(audio_data)} 字节")

                if audio_data:
                    # 写入WAV文件
                    with wave.open(path, "wb") as wav_file:
                        wav_file.setnchannels(channels or 1)
                        wav_file.setsampwidth(sample_width or 2)
                        wav_file.setframerate(sample_rate or 22050)
                        wav_file.writeframes(audio_data)

                    info(f"方法1成功，写入WAV文件: {path}")
                else:
                    warning("方法1: 没有收集到音频数据")
                    raise RuntimeError("没有音频数据")

            except Exception as method1_error:
                warning(f"方法1失败: {method1_error}")

                # 方法2: 使用synthesize_wav()并设置WAV参数
                info("尝试方法2: 使用synthesize_wav()...")
                try:
                    with wave.open(path, "wb") as wav_file:
                        # 先设置WAV参数（使用默认值）
                        wav_file.setnchannels(1)
                        wav_file.setsampwidth(2)
                        wav_file.setframerate(22050)

                        # 调用synthesize_wav
                        voice.synthesize_wav(text, wav_file)

                    info(f"方法2完成，文件大小: {os.path.getsize(path)} 字节")

                except Exception as method2_error:
                    warning(f"方法2失败: {method2_error}")

                    # 方法3: 回退到原始方法 (voice.synthesize(text, file_obj))
                    info("尝试方法3: 回退到原始方法...")
                    try:
                        with open(path, "wb") as f:
                            voice.synthesize(text, f)

                        info(f"方法3完成，文件大小: {os.path.getsize(path)} 字节")

                    except Exception as method3_error:
                        error(f"所有方法都失败: {method3_error}")
                        raise RuntimeError(f"所有Piper TTS合成方法都失败: {method3_error}")

            # 验证文件是否成功创建
            if not os.path.exists(path):
                raise RuntimeError(f"Failed to create audio file at {path}")

            file_size = os.path.getsize(path)
            if file_size == 0:
                warning(f"Created empty audio file at {path} - keeping for inspection")
            else:
                info(f"Generated audio file: {path}, size: {file_size} bytes")

            return path

        except Exception as e:
            error(f"Failed to generate speech: {e}")
            # 如果文件创建失败，尝试清理
            if os.path.exists(path):
                try:
                    os.remove(path)
                except:
                    pass
            raise RuntimeError(f"Piper TTS synthesis failed: {e}")

    async def generate_async(self, text, output="output.wav"):
        """异步包装的 TTS 生成函数，将阻塞操作放入线程池执行。"""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.generate, text, output)

    def generate_files(self, text, output_prefix="output"):
        """
        为向后兼容性提供的方法。
        返回包含单个文件路径的列表以保持接口兼容。
        """
        # 生成单个文件，使用output_prefix作为基础名
        output_file = f"{output_prefix}.wav"
        file_path = self.generate(text, output_file)
        return [file_path]