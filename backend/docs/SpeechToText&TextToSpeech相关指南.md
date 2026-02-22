# SpeechToText&TextToSpeech相关指南

## 前言

python版本:3.10.13

系统:Arch Linux

全部跑在cpu上，对性能占用实测不高

## SpeechToText

### 库

`sherpa-onnx`

安装

```bash
pip install sherpa-onnx
```

### 模型

类型

**Transducer**

- Zipformer
- Conformer
- Emformer

**Paraformer**

- 适合离线批处理

**Whisper**

- 支持 90+ 语言
- 适合多语言场景

建议使用zipformer模型或paraformer模型，使用wget命令进行下载：

```bash
# Zipformer 中英双语
wget https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-streaming-zipformer-bilingual-zh-en-2023-02-20.tar.bz2
```

```bash
# Paraformer 中英双语
wget https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-streaming-paraformer-bilingual-zh-en.tar.bz2
```

为降低占用，这里使用paraformer模型

解压后，你的模型结构应该如下：

```
models/
├── test_wavs/
├── decoder.int8.onnx
├── decoder.onnx
├── encoder.int8.onnx
├── encoder.onnx
├── README.md
└── tokens.txt
```

- `decorder.onnx`  解码器
- `encorder.onnx`  编码器
- `tokens token`对应表
- `test_waves/`  测试音频
- `*.int8.onnx` 经过int8量化过的模型

### 使用说明

识别器声明：

```python
import sherpa_onnx
import soundfile as sf #这是音频处理库，后面会用到
recognizer = sherpa_onnx.OnlineRecognizer.from_paraformer(
            tokens=os.path.join(model_dir, "tokens.txt"),
            encoder=os.path.join(model_dir, "encoder.onnx"),
            decoder=os.path.join(model_dir, "decoder.onnx"),
            num_threads=4,
            sample_rate=16000,
            feature_dim=80,
        )
```

- `model_dir` 你的模型路径
- `tokens`, `encoder` ,`decoder` 全部与模型文件夹内的模型对应
- `num_threads` 线程数
- `sample_rate` 采样率
- `feature_dim` 特征维度，越高识别能力越强，同时性能消耗越大

创建音频流：

```python
audio, sr = sf.read(self.audio_path)
stream = recognizer.create_stream()
stream.accept_waveform(self.sample_rate, audio)
```

识别并获取结果：

```python
while recognizer.is_ready(stream):
	recognizer.decode_stream(stream)
result = recognizer.get_result(stream)
```



## TextToSpeech

### 库

MeloTTS

注意，该库未加入官方镜像源，仅能从github下载安装

```bash
pip install git+https://github.com/myshell-ai/MeloTTS.git
```

安装完后，请安装字典unidic，否则无法过启动时自检

```bash
python -m unidic download
```

### 模型

第一次使用时会自动从hugging face下载模型，但是下载速度奇慢，所以建议使用镜像：

设置环境变量

```bash
export HF_ENDPOINT=https://hf-mirror.com
```

或在代码前添加

```python
# 使用国内镜像（放在 import melo 之前）
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
```

### 使用说明

合成器声明:

```python
from melo.api import TTS
tts = TTS(language = "ZH",device = "cpu")
```

合成音频并输出：

```python
tts.tts_to_file(sentence,speaker_id=0,output_path=temp_path)
audio , sr = sf.read(temp_path)
sf.write(file_name, audio, sample_rate)
```