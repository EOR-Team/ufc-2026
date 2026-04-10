# llama-cpp-python 服务器部署指南

## 概述

llama-cpp-python 提供 OpenAI 兼容的 Web 服务器，可以直接替代 OpenAI API 使用，支持流式输出、多模态、嵌入等功能。

---

## 快速启动

### 基础服务器

```bash
# 安装服务器组件
pip install 'llama-cpp-python[server]'

# 启动服务器
python3 -m llama_cpp.server --model ./models/llama-model.gguf --port 8000
```

### GPU 加速

```bash
# CUDA 支持
python3 -m llama_cpp.server \
    --model ./models/llama-model.gguf \
    --n_gpu_layers 35 \
    --port 8000
```

### 从 Hugging Face 加载

```bash
# 直接从 HF 下载模型
python3 -m llama_cpp.server \
    --hf_model_repo_id lmstudio-community/Qwen3.5-0.8B-GGUF \
    --model '*Q8_0.gguf' \
    --port 8000
```

---

## 完整启动参数

```bash
python3 -m llama_cpp.server \
    --model ./models/llama-model.gguf \
    --chat_format chatml \
    --host 0.0.0.0 \
    --port 8000 \
    --n_gpu_layers -1 \
    --n_ctx 4096 \
    --n_threads 8 \
    --verbose
```

| 参数 | 说明 |
|------|------|
| `--model` | GGUF 模型文件路径 |
| `--hf_model_repo_id` | Hugging Face 仓库 ID |
| `--chat_format` | 聊天格式 (chatml, llama-2, llama-3, mistral-instruct) |
| `--host` | 监听地址 |
| `--port` | 监听端口 |
| `--n_gpu_layers` | GPU 加速层数 |
| `--n_ctx` | 上下文窗口大小 |
| `--n_threads` | CPU 线程数 |

---

## API 端点

### POST /v1/chat/completions

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-model",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Hello!"}
    ],
    "max_tokens": 256,
    "temperature": 0.7
  }'
```

**流式响应**:
```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-model",
    "messages": [{"role": "user", "content": "Tell me a story"}],
    "stream": true
  }'
```

### POST /v1/completions

```bash
curl http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-model",
    "prompt": "The capital of France is",
    "max_tokens": 50
  }'
```

### GET /v1/models

```bash
curl http://localhost:8000/v1/models
```

---

## 与 FastAPI/OpenAI 客户端集成

由于服务器完全兼容 OpenAI API，可以直接使用 OpenAI Python 客户端：

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="not-needed"  # 本地服务不需要 API key
)

# 聊天补全
chat_response = client.chat.completions.create(
    model="llama-model",
    messages=[
        {"role": "system", "content": "You are a medical assistant."},
        {"role": "user", "content": "I have a headache, what should I do?"}
    ],
    temperature=0.7,
    max_tokens=256
)
print(chat_response.choices[0].message.content)

# 文本补全
text_response = client.completions.create(
    model="llama-model",
    prompt="Once upon a time",
    max_tokens=100
)
print(text_response.choices[0].text)
```

### LangChain 集成

```python
from langchain_community.llms import LlamaCpp
from langchain_core.prompts import PromptTemplate

llm = LlamaCpp(
    model_path="./models/llama-model.gguf",
    n_ctx=2048,
    n_threads=8,
    temperature=0.7
)

template = """Question: {question}

Answer: Let me think step by step."""
prompt = PromptTemplate.from_template(template)

chain = prompt | llm
result = chain.invoke({"question": "What is the capital of France?"})
```

---

## systemd 服务配置 (Linux)

创建服务文件 `/etc/systemd/system/llama-server.service`:

```ini
[Unit]
Description=llama-cpp-python Server
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/llm
ExecStart=/home/pi/venv/bin/python3 -m llama_cpp.server \
    --model /home/pi/models/llama-model.gguf \
    --host 0.0.0.0 \
    --port 8000 \
    --n_gpu_layers -1 \
    --n_ctx 2048
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务:
```bash
sudo systemctl daemon-reload
sudo systemctl enable llama-server
sudo systemctl start llama-server
```

---

## Docker 部署

```dockerfile
FROM python:3.11-slim

RUN pip install 'llama-cpp-python[server]'

WORKDIR /app
COPY models/ ./models/

EXPOSE 8000

CMD ["python3", "-m", "llama_cpp.server", "--model", "models/model.gguf", "--host", "0.0.0.0"]
```

构建和运行:
```bash
docker build -t llama-server .
docker run -d --gpus all -p 8000:8000 -v /path/to/models:/app/models llama-server
```

---

## 性能调优

### CPU 推理优化

```bash
# 设置线程数
export OMP_NUM_THREADS=8

# 启动服务器
python3 -m llama_cpp.server \
    --model ./models/llama-model.gguf \
    --n_ctx 2048 \
    --n_threads 8 \
    --n_batch 512
```

### GPU 推理优化

```bash
# CUDA 完整加速
python3 -m llama_cpp.server \
    --model ./models/llama-model.gguf \
    --n_gpu_layers -1 \
    --n_ctx 4096
```

### 批处理优化

```python
# 客户端批处理
batch_prompts = ["prompt1", "prompt2", "prompt3"]
results = [llm(prompt) for prompt in batch_prompts]  # 串行处理
```

---

## 故障排查

### 模型加载失败

```
Error: failed to load model
```
- 检查 GGUF 文件路径是否正确
- 确认文件未损坏
- 验证模型格式是否与 llama-cpp-python 兼容

### CUDA 不可用

```
ggml_init: no CUDA device
```
- 确认 NVIDIA 驱动已安装: `nvidia-smi`
- 重新编译 with CUDA 支持
- 检查 CUDA_PATH 环境变量

### 内存不足 (OOM)

```
CUDA out of memory
```
- 减少 `n_gpu_layers`
- 使用更小的量化版本 (Q4_K_M 代替 Q6_K)
- 减少 `n_ctx` 大小

---

## 参考链接

- [llama-cpp-python 服务器文档](https://github.com/abetlen/llama-cpp-python/blob/main/README.md)
- [OpenAI 兼容 API](https://platform.openai.com/docs/api-reference)
