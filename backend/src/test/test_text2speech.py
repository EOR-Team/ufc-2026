#!/usr/bin/env python3
"""
文本转语音测试 - 使用新的Edge-TTS系统
"""

import sys
import os
import numpy as np
import soundfile as sf

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voice_interaction.text2speech import TextToSpeech

def test_basic_tts():
    """测试基本TTS功能"""
    print("测试基本TTS功能...")
    
    # 创建TTS实例
    tts = TextToSpeech(
        output_path="./backend/src/voice_interaction/output.wav"
    )
    
    # 测试中文文本
    text = "你好，这是一个文本转语音测试"
    output_path = tts.synthesize(text)
    
    # 验证文件存在
    assert os.path.exists(output_path), f"输出文件不存在: {output_path}"
    
    # 验证音频质量
    audio, sample_rate = sf.read(output_path)
    max_amplitude = np.max(np.abs(audio))
    
    print(f"音频合成完成，保存到: {output_path}")
    print(f"采样率: {sample_rate} Hz")
    print(f"最大振幅: {max_amplitude:.6f}")
    
    # 验证振幅正常（新系统应该>0.1）
    assert max_amplitude > 0.1, f"音频振幅过小: {max_amplitude:.6f} (应>0.1)"
    
    return True

def test_different_voices():
    """测试不同的声音"""
    print("\n测试不同的声音...")
    
    voices = ["zh-CN-XiaoxiaoNeural", "zh-CN-YunxiNeural"]
    
    for voice in voices:
        print(f"测试声音: {voice}")
        tts = TextToSpeech(
            voice=voice,
            output_path=f"./backend/src/voice_interaction/output_{voice}.wav"
        )
        
        text = "测试不同声音"
        output_path = tts.synthesize(text)
        
        assert os.path.exists(output_path), f"输出文件不存在: {output_path}"
        print(f"  ✓ {voice}: 成功")
    
    return True

def test_speed_adjustment():
    """测试语速调整"""
    print("\n测试语速调整...")
    
    tts = TextToSpeech(
        output_path="./backend/src/voice_interaction/output_speed.wav"
    )
    
    text = "测试语速调整功能"
    
    # 测试不同语速
    for speed in [0.8, 1.0, 1.2]:
        output_path = tts.synthesize_with_speed(text, speed)
        assert os.path.exists(output_path), f"输出文件不存在: {output_path}"
        print(f"  ✓ 语速 {speed:.1f}x: 成功")
    
    return True

def test_edge_tts_features():
    """测试Edge-TTS特有功能"""
    print("\n测试Edge-TTS特有功能...")
    
    # 测试参数调整
    tts = TextToSpeech(
        voice="zh-CN-XiaoxiaoNeural",
        rate="+20%",
        volume="+10%",
        output_path="./backend/src/voice_interaction/output_features.wav"
    )
    
    # 测试列表声音功能
    voices = tts.list_voices()
    assert len(voices) > 0, "应该能列出可用的声音"
    print(f"可用声音数量: {len(voices)}")
    
    # 测试设置功能
    tts.set_voice("zh-CN-YunxiNeural")
    tts.set_speed("-10%")
    
    text = "测试Edge-TTS功能"
    output_path = tts.synthesize(text)
    
    assert os.path.exists(output_path), f"输出文件不存在: {output_path}"
    print(f"  ✓ Edge-TTS功能: 正常")
    
    return True

def main():
    """主测试函数"""
    print("=" * 60)
    print("Edge-TTS系统测试")
    print("=" * 60)
    
    # 确保输出目录存在
    os.makedirs("./backend/src/voice_interaction", exist_ok=True)
    
    tests = [
        ("基本功能", test_basic_tts),
        ("不同声音", test_different_voices),
        ("语速调整", test_speed_adjustment),
        ("Edge-TTS功能", test_edge_tts_features),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            test_func()
            print(f"\n✅ {test_name}: 通过")
            passed += 1
        except Exception as e:
            print(f"\n❌ {test_name}: 失败 - {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("✅ 所有测试通过！")
        return 0
    else:
        print("❌ 部分测试失败")
        return 1

if __name__ == "__main__":
    exit(main())
