from voice_interaction.text2speech import TextToSpeech

def test_text_to_speech():
    print("初始化模型...")
    tts = TextToSpeech()  # ← 移到循环外，只初始化一次
    print("模型就绪！输入 'exit' 退出\n")
    
    while True:
        text = input("> ").strip()
        if text.lower() == "exit":
            break
        if not text:
            continue
        
        files = tts.generate_files(text)
        print(f"生成 {len(files)} 个文件\n")

if __name__ == "__main__":
    test_text_to_speech()