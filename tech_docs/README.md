# 技术文档索引

本文档目录包含 ufc-2026 项目所需的技术参考资料。

---

## 目录结构

```
tech_docs/
├── README.md              # 本索引文件
├── llama-cpp-python.md    # Python 绑定核心 API
├── llama-cpp-server.md    # OpenAI 兼容服务器部署
├── llama-cpp-api.md       # 详细 API 参考
├── lfm2.5-model.md        # LFM2.5-1.2B-Instruct 模型指南
└── QUANTIZATION.md        # 模型量化指南
```

---

## 快速导航

### llama-cpp-python 基础

| 文档 | 内容 |
|------|------|
| [llama-cpp-python.md](llama-cpp-python.md) | 安装、基本用法、模型加载、聊天补全 |
| [llama-cpp-api.md](llama-cpp-api.md) | 完整 API 参考、参数说明、低层 CFFI |

### 服务器部署

| 文档 | 内容 |
|------|------|
| [llama-cpp-server.md](llama-cpp-server.md) | OpenAI 兼容 API 部署、systemd 配置、Docker |

### LFM2.5-1.2B-Instruct

| 文档 | 内容 |
|------|------|
| [lfm2.5-model.md](lfm2.5-model.md) | 模型规格、部署方式、医疗问答应用 |

---

## 技术栈概览

```
部署需求:
┌─────────────────────────────────────────────────────────────┐
│                     树莓派 4B (4GB)                          │
├─────────────────────────────────────────────────────────────┤
│  LLM 推理:    llama-cpp-python + LFM2.5-1.2B-Instruct Q4_K_M │
│  STT:         whisper.cpp (base 模型)                        │
│  TTS:         Piper (zh_CN-medium)                          │
│  后端框架:     FastAPI + Pydantic                           │
│  前端:         Vue 3 + Vuetify 3                            │
└─────────────────────────────────────────────────────────────┘

上下文限制:
- LFM2.5 n_ctx: 2048
- system_tokens + user_tokens + max_tokens ≤ 2048
```

---

## 关键配置参数

### LFM2.5-1.2B-Instruct (Q4_K_M)

```python
llm = Llama(
    model_path="./models/lfm2.5-1.2b.q4_k_m.gguf",
    n_ctx=2048,          # 上下文窗口
    n_threads=4,         # 4GB RAM: 4 线程
    n_gpu_layers=0,      # 无 GPU
    temperature=0.3,     # 医疗场景低温度
)
```

### whisper.cpp (base 模型)

```bash
# 内存占用: ~200MB
# 速度: ~1.8x realtime
./whisper-cli -m models/ggml-base.bin -f audio.wav
```

### Piper TTS

```bash
# 中文语音合成
echo '你好' | piper --model zh_CN-medium.onnx --output_file test.wav
```

---

## 相关链接

### 官方文档

- [llama-cpp-python](https://abetlen.github.io/llama-cpp-python/)
- [llama.cpp](https://github.com/ggerganov/llama.cpp)
- [Piper TTS](https://github.com/rhasspy/piper)
- [whisper.cpp](https://github.com/ggerganov/whisper.cpp)

### 模型资源

- [LFM2.5 Ollama](https://ollama.com/library/lfm2.5)
- [Hugging Face GGUF](https://huggingface.co/models?filter=gguf)

---

*最后更新: 2026-04-10*
