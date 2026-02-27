# 后端安装指南

测试环境：Ubuntu 24.04 / Python 3.10.13 / CPU-only

---

## 一、系统前置依赖

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y build-essential cmake libopenblas-dev wget unzip
```

---

## 二、Python 环境

本项目**严格要求 Python 3.10.13**，推荐通过 pyenv 安装：

```bash
pyenv install 3.10.13
pyenv shell 3.10.13
```

确认版本：

```bash
python --version  # 应输出 Python 3.10.13
```

---

## 三、创建虚拟环境

```bash
cd backend
python -m venv ./venv
source ./venv/bin/activate
```

升级 pip：

```bash
pip install --upgrade pip
```

---

## 四、安装 Python 依赖

### 4.1 常规依赖

**CPU 推理（推荐）**，使用 OpenBLAS 加速 llama-cpp-python：

```bash
CMAKE_ARGS="-DGGML_BLAS=ON -DGGML_BLAS_VENDOR=OpenBLAS" \
    pip install -r requirements.txt --timeout 300
```

> `requirements.txt` 中包含一行 `.whl` 文件路径（MeloTTS），下一步单独处理。

**GPU 推理（不推荐）**：

```bash
# 前提：已安装 NVIDIA 驱动、CUDA Toolkit、cuDNN
CMAKE_ARGS="-DGGML_CUDA=on" pip install -r requirements.txt --timeout 300
```

### 4.2 安装 MeloTTS

MeloTTS 未发布到 PyPI，有两种方式：

**方式 A：使用本地 whl（推荐）**

将 `melotts-*.whl` 放在 `backend/` 目录下，然后：

```bash
pip install melotts-0.1.2-py3-none-any.whl
```

**方式 B：从 GitHub 安装**

```bash
export HF_ENDPOINT=https://hf-mirror.com
pip install git+https://github.com/myshell-ai/MeloTTS.git
```

### 4.3 修复 numpy 版本冲突

MeloTTS 的依赖链会将 numpy 降级到 1.26.x，但 opencv 要求 numpy >= 2。安装 MeloTTS 后**必须**执行：

```bash
pip install "numpy>=2"
```

---

## 五、配置 unidic 字典（MeloTTS 依赖）

MeloTTS 初始化时 MeCab 需要 unidic 字典，有以下两种处理方式：

**方式 A：使用 unidic_lite 软链接（推荐，无需下载）**

MeloTTS 已附带安装 `unidic_lite`，对中文 TTS 完全够用。只需将其软链接到 unidic 字典目录：

```bash
python - <<'PY'
import unidic_lite, unidic, os

lite_dir = unidic_lite.DICDIR
uni_dir  = unidic.DICDIR

if not os.path.isfile(os.path.join(uni_dir, "mecabrc")):
    if os.path.exists(uni_dir):
        os.remove(uni_dir)
    os.symlink(lite_dir, uni_dir)
    print(f"软链接已创建: {uni_dir} -> {lite_dir}")
else:
    print("unidic 已就绪，无需操作")
PY
```

**方式 B：下载完整 unidic（约 500MB）**

```bash
python -m unidic download
```

---

## 六、安装 NLTK 资源

MeloTTS 使用 NLTK 进行英文文本处理：

```bash
python - <<'PY'
import nltk, os, sys
download_dir = os.path.join(os.path.dirname(sys.executable), "..", "nltk_data")
nltk.download("averaged_perceptron_tagger_eng", download_dir=os.path.abspath(download_dir))
PY
```

---

## 七、配置 STT 模型（sherpa-onnx Paraformer）

项目使用 **sherpa-onnx-streaming-paraformer-bilingual-zh-en** 进行中英文语音识别。

模型目标路径：

```
backend/src/voice_interaction/models/sherpa-onnx-streaming-paraformer-bilingual-zh-en/
```

**方式 A：使用本地压缩包**

将 `sherpa-onnx-streaming-paraformer-bilingual-zh-en.tar.bz2` 放在 `backend/` 目录下，然后：

```bash
mkdir -p src/voice_interaction/models
tar -xjf sherpa-onnx-streaming-paraformer-bilingual-zh-en.tar.bz2 \
    -C src/voice_interaction/models/
```

**方式 B：从网络下载**

```bash
wget https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-streaming-paraformer-bilingual-zh-en.tar.bz2
mkdir -p src/voice_interaction/models
tar -xjf sherpa-onnx-streaming-paraformer-bilingual-zh-en.tar.bz2 \
    -C src/voice_interaction/models/
rm sherpa-onnx-streaming-paraformer-bilingual-zh-en.tar.bz2
```

解压后目录结构应如下：

```
src/voice_interaction/models/sherpa-onnx-streaming-paraformer-bilingual-zh-en/
├── encoder.onnx
├── encoder.int8.onnx
├── decoder.onnx
├── decoder.int8.onnx
├── tokens.txt
├── README.md
└── test_wavs/
```

必需文件：`encoder.onnx`、`decoder.onnx`、`tokens.txt`

---

## 八、配置离线 LLM 模型

将 GGUF 格式模型文件放置在 `backend/model/` 目录下：

| 文件名 | 用途 |
|--------|------|
| `LFM2.5-1.2B-Instruct-Q4_K_M.gguf` | 离线聊天模型（当前默认） |
| `Qwen3-4B-Thinking-2507-Q4_K_M.gguf` | 离线推理模型（可选） |

模型路径在 `src/config/general.py` 中统一配置，如需切换模型修改该文件即可。

---

## 九、配置环境变量

在 `backend/` 目录下创建 `.env` 文件：

```bash
cp .env.example .env
```

填写以下必要变量：

```ini
# DeepSeek API Key（在线模型必填）
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
```

---

## 十、其他资产

| 资产 | 路径 | 说明 |
|------|------|------|
| 人脸图像 | `backend/assets/face/face.png` | 用于人脸识别，需替换为实际人脸图像 |
| 地图数据 | `backend/assets/small1.map.json` | 导航图，已内置无需修改 |
| STT 音频缓冲 | `backend/assets/input.wav` | 系统自动写入，无需手动配置 |

---

## 十一、验证安装

运行一键验证脚本：

```bash
bash install_deps.sh
```

或手动验证关键模块：

```bash
python - <<'PY'
modules = [
    ("fastapi",          "FastAPI"),
    ("llama_cpp",        "llama-cpp-python"),
    ("openai",           "OpenAI"),
    ("pydantic",         "Pydantic"),
    ("sherpa_onnx",      "sherpa-onnx (STT)"),
    ("soundfile",        "soundfile"),
    ("cv2",              "opencv-python"),
    ("face_recognition", "face_recognition"),
    ("numpy",            "numpy"),
    ("melo",             "MeloTTS (TTS)"),
]
for mod, name in modules:
    try:
        __import__(mod)
        print(f"  [✓] {name}")
    except ImportError as e:
        print(f"  [✗] {name}: {e}")
PY
```

---

## 十二、启动服务

```bash
cd backend
source venv/bin/activate

# 启动 FastAPI 主服务（端口 8000）
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

服务启动时会自动执行以下预热操作：
1. 清除系统代理环境变量（防止本地 API 被拦截）
2. 加载离线聊天模型（LFM2.5）到内存
3. 初始化语音交互模块（STT + TTS）

首次启动预热约需 **15~30 秒**，属正常现象。

---

## 常见问题

| 现象 | 原因 | 解决方案 |
|------|------|---------|
| `numpy` 版本报错 | MeloTTS 将 numpy 降级 | 重新运行 `pip install "numpy>=2"` |
| MeCab / unidic 报错 | unidic 字典缺失 | 参考[第五节](#五配置-unidic-字典melotts-依赖)创建软链接 |
| `llama_decode returned -1` | LFM2.5 KV cache 异常 | 已在代码中通过 `model.reset()` 修复，升级代码至最新即可 |
| 离线模型 segfault | token 总数超出 `n_ctx` | 检查 system prompt + user input + max_tokens 总量不超过 4096 |
| STT 模型文件缺失 | 模型未放置到正确路径 | 参考[第七节](#七配置-stt-模型sherpa-onnx-paraformer)重新配置 |
| 在线 API 请求失败 | 系统代理拦截了本地请求 | 服务启动时自动清除代理，若仍失败请检查防火墙设置 |
