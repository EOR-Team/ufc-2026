import sherpa_onnx
import os
import asyncio
import soundfile as sf


class SpeechRecognizer:
    def __init__(
        self,
        model_dir=None,
        audio_path="./assets/input.wav",
        sample_rate=16000,
    ):
        # 如果未显式提供 model_dir，使用相对于本模块的 models 目录（包内路径）
        if model_dir is None:
            base = os.path.dirname(__file__)
            model_dir = os.path.join(base, "models", "sherpa-onnx-streaming-paraformer-bilingual-zh-en")
        self.model_dir = model_dir
        # 延迟初始化 recognizer，避免在实例化时因模型文件缺失抛出异常
        self.recognizer = None
        self.audio_path = audio_path
        self.sample_rate = sample_rate

    def _create_recognizer(self):
        recognizer = sherpa_onnx.OnlineRecognizer.from_paraformer(
            tokens=os.path.join(self.model_dir, "tokens.txt"),
            encoder=os.path.join(self.model_dir, "encoder.onnx"),
            decoder=os.path.join(self.model_dir, "decoder.onnx"),
            num_threads=1,
            sample_rate=16000,
            feature_dim=80,
        )
        return recognizer

    def _ensure_recognizer(self):
        """如果 recognizer 还未创建，则创建它（在需要时调用）。"""
        if self.recognizer is None:
            self.recognizer = self._create_recognizer()

    async def recognize_async(self):
        """异步识别接口。

        将阻塞的文件读取和解码循环通过 `asyncio` 的线程池执行，
        从而不会阻塞事件循环。返回 recognizer 的结果对象。
        """
        loop = asyncio.get_running_loop()

        if not os.path.exists(self.audio_path):
            raise FileNotFoundError(f"Audio file {self.audio_path} not found")

        # 在线程池中读取音频，避免阻塞事件循环
        audio, sr = await loop.run_in_executor(None, sf.read, self.audio_path)
        if sr != self.sample_rate:
            raise ValueError(f"Expected sample rate {self.sample_rate}, but got {sr}")

        # 在线程池中创建 stream 并接收波形数据
        def _create_and_accept():
            stream = self.recognizer.create_stream()
            stream.accept_waveform(self.sample_rate, audio)
            return stream

        # 确保 recognizer 已初始化（可能会在此处抛出缺少模型文件的异常）
        await loop.run_in_executor(None, self._ensure_recognizer)
        stream = await loop.run_in_executor(None, _create_and_accept)

        # 将阻塞的解码循环放到线程池中执行
        def _decode_loop_and_get_result():
            while self.recognizer.is_ready(stream):
                self.recognizer.decode_stream(stream)
            return self.recognizer.get_result(stream)

        result = await loop.run_in_executor(None, _decode_loop_and_get_result)
        return result
