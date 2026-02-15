#!/usr/bin/env python3
"""
文本转语音模块 - 基于Edge-TTS

此模块替换了原来的sherpa-onnx实现，解决了音频振幅过小的问题。
使用微软Edge浏览器的TTS引擎，提供高质量的语音合成。
"""

import asyncio
import edge_tts
import os
import numpy as np
import soundfile as sf
from typing import Optional, Dict

class TextToSpeech:
    """
    文本转语音类（兼容旧接口）
    
    注意：这个类替换了原来的sherpa-onnx实现，使用Edge-TTS。
    接口保持兼容，但内部实现完全不同。
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
        model_dir: Optional[str] = None,  # 保持兼容性，但不再使用
        output_path: str = "./voice_interaction/output.wav",
        sample_rate: int = 24000,  # Edge-TTS默认采样率
        voice: str = "zh-CN-XiaoxiaoNeural",
        rate: str = "+0%",  # 语速调整
        volume: str = "+0%",  # 音量调整
        pitch: str = "+0Hz",  # 音调调整
    ):
        """
        初始化文本转语音
        
        Args:
            model_dir: 模型目录（已弃用，为保持兼容性保留）
            output_path: 输出文件路径
            sample_rate: 采样率（Edge-TTS固定为24000）
            voice: 声音ID
            rate: 语速调整
            volume: 音量调整
            pitch: 音调调整
        """
        # 为保持兼容性，忽略model_dir参数
        if model_dir:
            print(f"注意: model_dir参数已弃用，Edge-TTS无需本地模型")
        
        self.output_path = output_path
        self.sample_rate = sample_rate
        self.voice = voice
        self.rate = rate
        self.volume = volume
        self.pitch = pitch
        
        # 创建输出目录
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # 验证声音
        if voice not in self.VOICES:
            print(f"警告: 声音 '{voice}' 不在预定义列表中，但Edge-TTS可能会支持")
        
        print(f"Edge-TTS初始化完成")
        print(f"使用声音: {voice} ({self.VOICES.get(voice, '自定义声音')})")
    
    async def _synthesize_async(self, text: str) -> str:
        """异步合成语音"""
        # 创建communicate对象
        communicate = edge_tts.Communicate(
            text=text,
            voice=self.voice,
            rate=self.rate,
            volume=self.volume,
            pitch=self.pitch,
        )
        
        # 保存音频文件
        await communicate.save(self.output_path)
        
        return self.output_path
    
    def synthesize(self, text: str) -> str:
        """
        合成语音（兼容旧接口）
        
        Args:
            text: 要合成的文本
            
        Returns:
            音频文件路径
        """
        self.text = text
        
        # 运行异步任务
        output_path = asyncio.run(self._synthesize_async(text))
        
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
    
    def synthesize_with_speed(self, text: str, speed: float = 1.0) -> str:
        """
        以指定语速合成语音（兼容旧接口）
        
        Args:
            text: 要合成的文本
            speed: 语速倍数（1.0为正常，>1.0加快，<1.0减慢）
            
        Returns:
            音频文件路径
        """
        # 保存原始语速设置
        original_rate = self.rate
        
        try:
            # 计算新的语速设置
            # Edge-TTS使用百分比，例如 +10% 表示加快10%
            if speed > 1.0:
                rate_percent = int((speed - 1.0) * 100)
                self.rate = f"+{rate_percent}%"
            elif speed < 1.0:
                rate_percent = int((1.0 - speed) * 100)
                self.rate = f"-{rate_percent}%"
            else:
                self.rate = "+0%"
            
            print(f"设置语速: {speed:.1f}x ({self.rate})")
            
            return self.synthesize(text)
            
        finally:
            # 恢复原始语速设置
            self.rate = original_rate
    
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


# 兼容性函数
def create_tts_instance():
    """创建TTS实例（兼容旧代码）"""
    return TextToSpeech()


def test_compatibility():
    """测试兼容性"""
    print("=" * 60)
    print("兼容性测试")
    print("=" * 60)
    
    # 使用旧接口创建实例
    tts = TextToSpeech(
        model_dir="voice_interaction/vits-melo-tts-zh_en",  # 这个参数会被忽略
        output_path="./voice_interaction/output_compat.wav"
    )
    
    # 测试文本
    text = "你好，这是兼容性测试"
    
    # 使用旧方法合成
    output_file = tts.synthesize(text)
    print(f"\n输出文件: {output_file}")
    
    # 测试带语速的方法
    print(f"\n测试不同语速:")
    for speed in [0.8, 1.0, 1.2]:
        output_file = tts.synthesize_with_speed(text, speed)
        print(f"  语速 {speed:.1f}x: {output_file}")

if __name__ == "__main__":
    test_compatibility()