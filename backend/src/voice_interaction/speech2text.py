import sherpa_onnx
import os
import soundfile as sf


class SpeechRecognizer:
    def __init__(
        self,
        model_dir="./voice_interaction/models/sherpa-onnx-streaming-paraformer-bilingual-zh-en",
        audio_path="./voice_interaction/input/sound.wav",
        sample_rate=16000,
    ):
        self.model_dir = model_dir
        self.recognizer = self._create_recognizer()
        self.audio_path = audio_path
        self.sample_rate = sample_rate

    def _create_recognizer(self):
        recognizer = sherpa_onnx.OnlineRecognizer.from_paraformer(
            tokens=os.path.join(self.model_dir, "tokens.txt"),
            encoder=os.path.join(self.model_dir, "encoder.onnx"),
            decoder=os.path.join(self.model_dir, "decoder.onnx"),
            num_threads=4,
            sample_rate=16000,
            feature_dim=80,
        )
        return recognizer

    def recognize(self):
        if not os.path.exists(self.audio_path):
            raise FileNotFoundError(f"Audio file {self.audio_path} not found")
        audio, sr = sf.read(self.audio_path)
        if sr != self.sample_rate:
            raise ValueError(f"Expected sample rate {self.sample_rate}, but got {sr}")
        stream = self.recognizer.create_stream()
        stream.accept_waveform(self.sample_rate, audio)
        while self.recognizer.is_ready(stream):
            self.recognizer.decode_stream(stream)
        return self.recognizer.get_result(stream)
