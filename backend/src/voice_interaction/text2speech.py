import os
import asyncio
from melo.api import TTS
import soundfile as sf
import re

os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'


class TextToSpeech:
    def __init__(self, path="../assets/output"):
        self._model = TTS(language="ZH", device="cpu")
        self.output_path = path
        self.sample_rate = self._model.hps.data.sampling_rate
        os.makedirs(self.output_path, exist_ok=True)

    def generate(self, text, output="output.wav"):
        path = os.path.join(self.output_path, output)
        self._model.tts_to_file(text, speaker_id=0, output_path=path)
        return path

    async def generate_async(self, text, output="output.wav"):
        """异步包装的 TTS 生成函数，将阻塞操作放入线程池执行。"""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.generate, text, output)