# 语音交互模块

## 概述

本模块提供文本转语音(TTS)和语音转文本(STT)功能。

## 当前状态

✅ **TTS系统已升级**：使用Edge-TTS替换了原来的sherpa-onnx实现，解决了音频振幅过小的问题。

## 文件结构

```
voice_interaction/
├── text2speech.py          # 主TTS模块（基于Edge-TTS）
├── text2speech_backup.py   # 原始sherpa-onnx实现备份
├── speech2text.py          # STT模块
├── requirements.txt        # 依赖文件
├── HANDOVER.md            # 交接文档
└── __init__.py           # 包初始化文件
```

## 快速开始

### 安装依赖

```bash
# 在项目根目录下
source .venv/bin/activate
pip install -r backend/src/voice_interaction/requirements.txt
```

### 使用TTS

```python
from voice_interaction.text2speech import TextToSpeech

# 创建TTS实例
tts = TextToSpeech(output_path="./output.wav")

# 合成语音
audio_file = tts.synthesize("你好，欢迎使用语音合成")
print(f"音频已保存: {audio_file}")
```

### 使用STT

```python
from voice_interaction.speech2text import SpeechToText

# 创建STT实例
stt = SpeechToText()

# 识别语音
text = stt.transcribe("audio_file.wav")
print(f"识别结果: {text}")
```

## TTS系统说明

### 新系统特点

1. **高质量语音**：使用微软Edge浏览器的TTS引擎
2. **无需大模型**：无需下载本地模型文件
3. **多语言支持**：支持中文、英文及混合
4. **参数灵活**：可调整语速、音量、音调
5. **接口兼容**：保持与原系统相同的接口

### 音频质量对比

| 指标 | 原系统 | 新系统 | 改进 |
|------|--------|--------|------|
| 最大振幅 | 0.01-0.04 | 0.47-0.72 | 提高30倍 |
| 主观评价 | 像"乱说" | 清晰自然 | 显著改善 |
| 部署复杂度 | 需要170MB模型 | 只需Python包 | 大幅简化 |

## 测试

运行测试：
```bash
cd /home/aunnno/Desktop/ufc-2026
.venv/bin/python backend/src/test/test_text2speech.py
```

实验性代码位于：`backend/src/test/tts_experiments/`

## 注意事项

1. **网络要求**：Edge-TTS需要访问微软的TTS服务
2. **声音选择**：推荐使用 `zh-CN-XiaoxiaoNeural`（中文女性）
3. **输出目录**：确保输出目录有写入权限

## 故障排除

### 常见问题

1. **无法生成音频**：检查网络连接
2. **导入错误**：确保已安装所有依赖
3. **权限错误**：检查输出目录权限

### 依赖列表

- `edge-tts`: TTS引擎
- `soundfile`: 音频文件处理
- `numpy`: 数值计算
- `sherpa-onnx`: STT功能（保留）

---

*最后更新：2024年2月15日*
*状态：✅ TTS问题已解决*