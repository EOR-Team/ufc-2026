#!/usr/bin/env python3
"""
基于Edge-TTS的文本转语音实现
使用微软Edge浏览器的TTS引擎，支持中英文
"""

import asyncio
import edge_tts
import os
import numpy as np
import soundfile as sf
from typing import Optional, List, Dict

class TextToSpeechEdge:
    """
    Edge-TTS文本转语音类
    
    特点：
    - 使用微软Edge浏览器的TTS引擎
    - 高质量语音合成
    - 支持中英文混合
    - 无需下载大模型
    - 免费使用
    """
    
    # 预定义的声音列表
    VOICES = {
        # 中文声音
        "zh-CN-XiaoxiaoNeural": "中文女性 - 晓晓（自然）",
        "zh-CN-XiaoyiNeural": "中文女性 - 晓伊（活泼）",
        "zh-CN-YunjianNeural": "中文男性 - 云健",
        "zh-CN-YunxiNeural": "中文男性 - 云希",
        "zh-CN-YunxiaNeural": "中文男性 - 云夏",
        "zh-CN-YunyangNeural": "中文男性 - 云扬",
        
        # 英文声音
        "en-US-JennyNeural": "英文女性 - Jenny",
        "en-US-GuyNeural": "英文男性 - Guy",
        "en-US-AriaNeural": "英文女性 - Aria",
        "en-US-DavisNeural": "英文男性 - Davis",
        
        # 中英双语声音
        "zh-CN-XiaoxiaoMultilingualNeural": "中英双语女性 - 晓晓多语言",
        "zh-CN-XiaoyiMultilingualNeural": "中英双语女性 - 晓伊多语言",
    }
    
    def __init__(
        self,
        voice: str = "zh-CN-XiaoxiaoNeural",
        output_dir: str = "./voice_interaction/output",
        rate: str = "+0%",  # 语速调整
        volume: str = "+0%",  # 音量调整
        pitch: str = "+0Hz",  # 音调调整
    ):
        """
        初始化Edge-TTS
        
        Args:
            voice: 声音ID，参考VOICES字典
            output_dir: 输出目录
            rate: 语速调整（例如："+10%" 加快，"-10%" 减慢）
            volume: 音量调整（例如："+10%" 增大，"-10%" 减小）
            pitch: 音调调整（例如："+10Hz" 提高，"-10Hz" 降低）
        """
        self.voice = voice
        self.output_dir = output_dir
        self.rate = rate
        self.volume = volume
        self.pitch = pitch
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 验证声音
        if voice not in self.VOICES:
            print(f"警告: 声音 '{voice}' 不在预定义列表中，但Edge-TTS可能会支持")
            
        print(f"Edge-TTS初始化完成")
        print(f"使用声音: {voice} ({self.VOICES.get(voice, '自定义声音')})")
    
    async def _synthesize_async(self, text: str, output_filename: str) -> str:
        """异步合成语音"""
        output_path = os.path.join(self.output_dir, output_filename)
        
        # 创建communicate对象
        communicate = edge_tts.Communicate(
            text=text,
            voice=self.voice,
            rate=self.rate,
            volume=self.volume,
            pitch=self.pitch,
        )
        
        # 保存音频文件
        await communicate.save(output_path)
        
        return output_path
    
    def synthesize(self, text: str, output_filename: Optional[str] = None) -> str:
        """
        同步合成语音
        
        Args:
            text: 要合成的文本
            output_filename: 输出文件名（可选，默认自动生成）
            
        Returns:
            音频文件路径
        """
        if output_filename is None:
            # 自动生成文件名
            import hashlib
            text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
            output_filename = f"tts_{text_hash}.wav"
        
        # 运行异步任务
        output_path = asyncio.run(self._synthesize_async(text, output_filename))
        
        # 分析音频质量
        self._analyze_audio(output_path, text)
        
        return output_path
    
    def _analyze_audio(self, filepath: str, text: str):
        """分析音频质量"""
        try:
            audio, sample_rate = sf.read(filepath)
            
            # 计算统计信息
            max_amplitude = np.max(np.abs(audio))
            rms = np.sqrt(np.mean(audio**2))
            duration = len(audio) / sample_rate
            
            print(f"\n音频生成成功:")
            print(f"  文本: '{text[:50]}{'...' if len(text) > 50 else ''}'")
            print(f"  保存到: {filepath}")
            print(f"  时长: {duration:.2f} 秒")
            print(f"  采样率: {sample_rate} Hz")
            print(f"  最大振幅: {max_amplitude:.6f}")
            print(f"  RMS: {rms:.6f}")
            
            # 质量检查
            if max_amplitude < 0.1:
                print(f"  ⚠️  警告: 音频振幅偏小")
            elif max_amplitude > 0.9:
                print(f"  ⚠️  警告: 音频振幅可能过大（接近削波）")
            else:
                print(f"  ✅ 音频质量正常")
                
        except Exception as e:
            print(f"分析音频时出错: {e}")
    
    def list_voices(self) -> Dict[str, str]:
        """列出所有可用的声音"""
        return self.VOICES.copy()
    
    def set_voice(self, voice: str):
        """设置声音"""
        self.voice = voice
        print(f"声音已设置为: {voice} ({self.VOICES.get(voice, '自定义声音')})")
    
    def set_speed(self, rate: str):
        """设置语速"""
        self.rate = rate
        print(f"语速已设置为: {rate}")
    
    def set_volume(self, volume: str):
        """设置音量"""
        self.volume = volume
        print(f"音量已设置为: {volume}")
    
    def set_pitch(self, pitch: str):
        """设置音调"""
        self.pitch = pitch
        print(f"音调已设置为: {pitch}")


def test_edge_tts():
    """测试函数"""
    print("=" * 60)
    print("Edge-TTS 测试")
    print("=" * 60)
    
    # 创建TTS实例
    tts = TextToSpeechEdge(
        voice="zh-CN-XiaoxiaoNeural",
        output_dir="./voice_interaction/output"
    )
    
    # 测试文本
    test_cases = [
        ("你好，欢迎使用Edge-TTS语音合成系统", "test_chinese.wav"),
        ("Hello, this is Edge-TTS text-to-speech system", "test_english.wav"),
        ("你好世界，Hello world，混合中英文测试", "test_mixed.wav"),
    ]
    
    for text, filename in test_cases:
        print(f"\n合成: '{text}'")
        try:
            output_path = tts.synthesize(text, filename)
            print(f"✓ 成功: {output_path}")
        except Exception as e:
            print(f"✗ 失败: {e}")
    
    # 列出可用声音
    print("\n" + "=" * 60)
    print("可用声音列表:")
    print("=" * 60)
    voices = tts.list_voices()
    for voice_id, description in voices.items():
        print(f"{voice_id}: {description}")

if __name__ == "__main__":
    test_edge_tts()