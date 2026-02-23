from .speech2text import SpeechRecognizer
from .text2speech import TextToSpeech
import os
import asyncio


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class VoiceInteraction(metaclass=SingletonMeta):
    def __init__(self):
        self.speech_recognizer = SpeechRecognizer()
        self.text_to_speech = TextToSpeech()
        # 如果需要预热，请调用 `await VoiceInteraction.warmup()`。

    async def warmup(self):
        """可选的异步预热方法，生成一个临时音频文件以触发模型加载。"""
        path = await self.text_to_speech.generate_async("测试用音频")
        # 在线程池或事件循环外部执行文件删除以避免阻塞
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, os.remove, path)

    def tts(self, text, output=None):
        return self.text_to_speech.generate(text)
    async def tts_async(self, text, output=None):
        return await self.text_to_speech.generate_async(text, output or "output.wav")

    async def stt_async(self):
        return await self.speech_recognizer.recognize_async()