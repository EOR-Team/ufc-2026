# Voice Module Design for Raspberry Pi 4B

本文档为 ufc-2026 项目在树莓派 4B (4GB) 平台上的语音交互模块设计。

## 目标平台

| 规格 | 数值 |
|------|------|
| 设备 | Raspberry Pi 4B |
| 内存 | 4GB |
| 存储 | 32GB+ microSD |
| 系统 | Raspberry Pi OS 64-bit (Bookworm) |
| 网络 | 可离线运行 |

## 方案选择

经过调研，推荐以下轻量级组合：

| 模块 | 推荐方案 | 备选方案 |
|------|---------|---------|
| **STT** (语音识别) | whisper.cpp | faster-whisper, Silero |
| **TTS** (语音合成) | Piper | Coqui TTS, espeak-ng |

---

## STT: Whisper.cpp

### 为什么选择 whisper.cpp

| 对比项 | OpenAI Whisper (PyTorch) | whisper.cpp |
|--------|-------------------------|-------------|
| 内存占用 | 3-4GB (加载前) | <500MB |
| 推理方式 | CUDA/CPU | 纯 C/C++ 原生 |
| 模型格式 | PyTorch .pt | GGML 量化 |
| Pi 4 适配 | ❌ 需大量 swap | ✅ 原生 ARM64 |

whisper.cpp 是 OpenAI Whisper 的 C/C++ 重写版，专门为资源受限设备优化。

### 支持的模型

| 模型 | 大小 | 内存占用 | 速度 (Pi 4) | 适用场景 |
|------|------|---------|-------------|---------|
| tiny | ~75MB | <200MB | ~0.9x realtime | 英文、实时对话 |
| tiny.en | ~75MB | <200MB | ~0.9x realtime | 英文专用、更快 |
| base | ~145MB | ~200MB | ~1.8x realtime | 多语言、通用 |
| base.en | ~145MB | ~200MB | ~1.8x realtime | 英文专用 |
| small | ~465MB | ~600MB | ~0.5x realtime | 高精度需求 |

**Pi 4B 4GB 推荐**: `base` 模型（多语言支持，包含中文）

### 安装步骤

```bash
# 1. 克隆 whisper.cpp
git clone https://github.com/ggerganov/whisper.cpp.git
cd whisper.cpp

# 2. 编译 (需要 ARM64 优化)
make clean
make -j$(nproc)

# 3. 下载模型
./models/download-ggml-model.sh base

# 4. 测试
./build/src/whisper-cli -m models/ggml-base.bin -f samples/jfk.wav
```

### Python 集成

```python
# 使用 pywhispercpp (Python 绑定)
pip install pywhispercpp

# 基本用法
from pywhispercpp.model import Model

model = Model("base")
result = model.transcribe("audio.wav")
print(result.text)
```

### 实时语音识别

```bash
# 使用 stream 模式实现实时识别
./build/src/whisper-cli -m models/ggml-base.bin \
  -f audio_input.wav \
  --step 2500 \
  --length 10000
```

---

## TTS: Piper

### 为什么选择 Piper

| 特性 | 说明 |
|------|------|
| 优化目标 | 专为树莓派优化 |
| 模型格式 | ONNX (跨平台) |
| 推理引擎 | onnxruntime |
| 音质 | VITS 神经网络，接近真人 |
| 中文支持 | ✅ 有官方中文模型 |

Piper 是 Rhasspy 开发的本地神经 TTS 系统，使用 VITS (Variational Inference for Text-to-Speech) 模型。

### 支持的语音

| 语音 | 大小 | 语言 | 音质 |
|------|------|------|------|
| en_US-lessac-medium | ~50MB | 英文 | 高 |
| en_US-lessac-large | ~100MB | 英文 | 极高 |
| zh_CN | ~80MB | 中文 | 高 |

### 安装步骤

```bash
# 1. 安装 Piper (Python)
pip install piper-tts

# 2. 下载中文语音模型
mkdir -p piper_models
cd piper_models

# 中文模型 (约 80MB)
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/zh_CN/medium/zh_CN-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/zh_CN/medium/zh_CN-medium.onnx.json

# 3. 测试
echo '你好，这是语音合成测试。' | piper \
  --model zh_CN-medium.onnx \
  --output_file test.wav
```

### Python 集成

```python
import piper

# 同步方式
piper.speak("你好，这是语音合成测试。", voice="zh_CN-medium")

# 或直接使用 onnxruntime
import onnxruntime as ort

session = ort.InferenceSession("zh_CN-medium.onnx")
# ... 完整示例见 piper 文档
```

---

## 架构设计

### 数据流

```
┌─────────────────────────────────────────────────────────────┐
│                        语音输入                              │
│                    (麦克风采集)                               │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    VAD (语音活动检测)                        │
│              WebRTC VAD / silero-vad                        │
└─────────────────────┬─────────────────────────────────────┘
                      │ 检测到语音开始
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  whisper.cpp (STT)                          │
│                  base 模型, ~145MB                          │
│                  Pi 4 上 ~1.8x realtime                     │
└─────────────────────┬─────────────────────────────────────┘
                      │ 文本输出
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    LLM 处理                                 │
│              (当前项目的 smart_triager)                      │
└─────────────────────┬─────────────────────────────────────┘
                      │ 文本响应
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    Piper (TTS)                              │
│                  zh_CN-medium 模型, ~80MB                   │
└─────────────────────┬─────────────────────────────────────┘
                      │ 音频输出
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    音频播放                                 │
│                  (aplay / pygame)                           │
└─────────────────────────────────────────────────────────────┘
```

### 模块接口设计

```python
# voice_engine.py

class VoiceEngine:
    """树莓派语音引擎"""

    def __init__(self):
        # STT: whisper.cpp
        self.stt_model = WhisperModel("base")

        # TTS: Piper
        self.tts_voice = "zh_CN-medium"

    async def speech_to_text(self, audio_path: str) -> str:
        """语音转文字"""
        result = self.stt_model.transcribe(audio_path)
        return result.text

    async def text_to_speech(self, text: str, output_path: str):
        """文字转语音"""
        cmd = f"echo '{text}' | piper --model {self.tts_voice} --output_file {output_path}"
        await subprocess.asyncio.run(cmd)

    async def process_voice_input(self, audio_path: str) -> str:
        """完整流程: 语音 → 文字 → LLM → 语音"""
        # 1. STT
        user_text = await self.speech_to_text(audio_path)

        # 2. LLM 处理 (调用现有的 smart_triager)
        response_text = await self.llm.process(user_text)

        # 3. TTS
        response_audio = "/tmp/response.wav"
        await self.text_to_speech(response_text, response_audio)

        return response_audio
```

---

## 资源评估

### 内存占用 (Pi 4B 4GB)

| 组件 | 内存占用 | 备注 |
|------|---------|------|
| 系统 | ~500MB | Raspberry Pi OS |
| whisper.cpp (base) | ~200MB | 含运行时 |
| Piper (zh_CN-medium) | ~150MB | 含 onnxruntime |
| LLM (如果本地) | ~1-2GB | 视模型大小 |
| 应用代码 | ~100MB | FastAPI + 其他 |
| **总计** | ~2-3GB | **安全范围内** |

### 存储占用

| 组件 | 大小 |
|------|------|
| whisper.cpp 二进制 | ~50MB |
| base 模型 | ~145MB |
| Piper 二进制 | ~30MB |
| zh_CN-medium 模型 | ~80MB |
| **总计** | ~305MB |

---

## 替代方案

### STT 替代

| 方案 | 优点 | 缺点 |
|------|------|------|
| **Silero** | 极轻量 (~50MB), 实时性好 | 精度略低 |
| **faster-whisper** | Python 友好, 内存优化 | 需要 PyTorch |
| **Vosk** | 专为嵌入式优化 | 模型较大 |

### TTS 替代

| 方案 | 优点 | 缺点 |
|------|------|------|
| **Coqui TTS** | 音质极高, 模型多 | 内存占用大 |
| **espeak-ng** | 极轻量 (<10MB) | 机械音, 无中文 |
| **MeloTTS** | 音质好, 有中文 | NumPy 版本冲突 |

---

## 参考资料

- [whisper.cpp GitHub](https://github.com/ggerganov/whisper.cpp)
- [Piper TTS GitHub](https://github.com/rhasspy/piper)
- [Piper 预训练模型](https://huggingface.co/rhasspy/piper-voices)
- [Whisper.cpp Pi 4 实时识别](https://www.youtube.com/watch?v=caaKhWcfcCY)
