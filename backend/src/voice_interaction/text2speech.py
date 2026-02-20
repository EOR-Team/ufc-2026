import os
from melo.api import TTS
import soundfile as sf

os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

class TextToSpeech:
    def __init__(self,output_dir="output"):
        self.tts = TTS(language="zh", device="cpu")
        self.sample_rate = self.tts.hps.data.sampling_rate
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def split_text(self, text):
        """按标点分割文本为句子"""
        sentences = re.split(r'([，。！？、；：])', text)
        result = []
        for i in range(0, len(sentences) - 1, 2):
            result.append(sentences[i] + sentences[i + 1])
        if len(sentences) % 2 == 1 and sentences[-1].strip():
            result.append(sentences[-1])
        return [s for s in result if s.strip()]
    

    def synthesize(self, text):
        sentences = self.split_text(text)
        for i,sentence in enumerate(sentences):
            temp_path = os.path.join(self.output_dir, f"temp_{i}.wav")
            self.tts.tts_to_file(sentence,speaker_id=0,output_path=temp_path)
            audio , sr = sf.read(temp_path)
            os.remove(temp_path)
            yield {
                'index': i,
                'text': sentence,
                'audio': audio,
                'sample_rate': sr
            }

    def tts(self,text):
        files = []
        for chunk in self.synthesize(text):
            file_name = os.path.join(self.output_dir, f"chunk_{chunk['index']}.wav")
            sf.write(file_name, chunk['audio'], chunk['sample_rate'])
            files.append(file_name)
        return files