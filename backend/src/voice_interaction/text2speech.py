import os
from melo.api import TTS
import soundfile as sf
import re

os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

class TextToSpeech:
    def __init__(self,path = "../assets/output"):
        self._model = TTS(language="ZH", device="cpu")
        self.output_path = path
        self.sample_rate = self._model.hps.data.sampling_rate
        os.makedirs(self.output_path, exist_ok=True)

    def generate(self,text,output="output.wav"):
        path = os.path.join(self.output_path, output)
        self._model.tts_to_file(text, speaker_id=0, output_path=path)
        return path