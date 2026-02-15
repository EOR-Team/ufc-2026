from backend.src.voice_interaction.speech2text import SpeechRecognizer

def test_speech_recognizer():
    recognizer = SpeechRecognizer()
    result = recognizer.recognize()
    assert isinstance(result, str)
    assert len(result) > 0
    print(f"Recognized text: {result}")

if __name__ == "__main__":
    test_speech_recognizer()
    print("All tests passed!")