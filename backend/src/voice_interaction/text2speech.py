import os
import asyncio
import soundfile as sf
import re

os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
from melo.api import TTS


class TextToSpeech:
    def __init__(self, path="./assets"):
        self._model = TTS(language="ZH", device="cpu")
        self.output_path = path
        self.sample_rate = self._model.hps.data.sampling_rate
        os.makedirs(self.output_path, exist_ok=True)

    def generate(self, text, output="output.wav"):
        path = os.path.join(self.output_path, output)
        # MeloTTS 中文 G2P 不支持 ASCII 字母和下划线，统一移除后清理多余空格
        text = re.sub(r'[a-zA-Z_]+', '', text)
        text = re.sub(r' +', ' ', text).strip()
        self._model.tts_to_file(text, speaker_id=0, output_path=path)
        return path

    async def generate_async(self, text, output="output.wav"):
        """异步包装的 TTS 生成函数，将阻塞操作放入线程池执行。"""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.generate, text, output)