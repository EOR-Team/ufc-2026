from .speech2text import SpeechRecognizer
from .text2speech import TextToSpeech
import os


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
        self.text_to_speech.generate("测试用音频")
        os.remove(os.path.join(self.text_to_speech.output_path, "output.wav"))

    def tts(self,text,output=None):
        return self.text_to_speech.generate(text)
    
    def stt(self):
        return self.speech_recognizer.recognize()