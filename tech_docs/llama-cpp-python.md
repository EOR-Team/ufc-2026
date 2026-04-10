# llama-cpp-python 技术文档

## 概述

`llama-cpp-python` 是 llama.cpp 的 Python 绑定，提供低层 C API 访问和高层 Python API，支持文本补全、聊天、嵌入功能，以及 OpenAI 兼容的 Web 服务器。

**GitHub**: https://github.com/abetlen/llama-cpp-python
**文档**: https://abetlen.github.io/llama-cpp-python/

---

## 安装

### CPU 版本（基础安装）

```bash
pip install llama-cpp-python
```

### CUDA GPU 加速

```bash
# 方法1：编译时启用 CUDA
CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python

# 方法2：使用预编译 wheel
pip install llama-cpp-python \
  --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121
```

### Apple Metal (macOS)

```bash
CMAKE_ARGS="-DGGML_METAL=on" pip install llama-cpp-python
```

### 服务器组件（OpenAI 兼容 API）

```bash
pip install 'llama-cpp-python[server]'
```

---

## 基础用法

### 模型加载

```python
from llama_cpp import Llama

# 基础模型加载
llm = Llama(
    model_path="./models/llama-model.gguf",
    n_ctx=2048,           # 上下文窗口大小
    n_gpu_layers=-1,      # GPU 加速层数 (-1 = 全部)
    n_threads=8,          # CPU 线程数
    verbose=False         # 禁用详细输出
)

# 带 chat format 加载
llm = Llama(
    model_path="./models/chat-model.gguf",
    chat_format="chatml",  # 可选: chatml, llama-2, llama-3, mistral-instruct
    n_ctx=4096
)

# 带嵌入支持加载
llm = Llama(
    model_path="./models/embedding-model.gguf",
    embedding=True,
    n_ctx=512
)

# LoRA 适配器
llm = Llama(
    model_path="./models/base-model.gguf",
    lora_path="./adapters/lora-adapter.bin",
    lora_scale=1.0,
    n_ctx=2048
)
```

### 文本补全

```python
# 基础补全
response = llm(
    "The capital of France is",
    max_tokens=128,
    temperature=0.7,
    top_p=0.9,
    top_k=40,
    echo=True
)
print(response["choices"][0]["text"])

# 流式输出
stream = llm(
    "Write a poem about AI:",
    stream=True,
    max_tokens=256
)
for chunk in stream:
    if "choices" in chunk and len(chunk["choices"]) > 0:
        print(chunk["choices"][0]["text"], end="", flush=True)
```

### 聊天补全

```python
response = llm.create_chat_completion(
    messages=[
        {"role": "system", "content": "You are a helpful medical assistant."},
        {"role": "user", "content": "What are symptoms of the common cold?"}
    ],
    max_tokens=256,
    temperature=0.7
)
print(response["choices"][0]["message"]["content"])

# 多轮对话
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is Python?"},
    {"role": "assistant", "content": "Python is a programming language."},
    {"role": "user", "content": "What is the latest version?"}
]
response = llm.create_chat_completion(messages=messages)
```

### 流式聊天补全

```python
stream = llm.create_chat_completion(
    messages=[{"role": "user", "content": "Tell me a joke"}],
    stream=True
)
for chunk in stream:
    delta = chunk["choices"][0]["delta"]
    if "content" in delta:
        print(delta["content"], end="", flush=True)
```

### 采样参数配置

```python
# 初始化采样链
llama_cpp.llama_sampler_chain_add(sampler_chain, llama_cpp.llama_sampler_init_top_k(40))
llama_cpp.llama_sampler_chain_add(sampler_chain, llama_cpp.llama_sampler_init_top_p(0.9, 1))
llama_cpp.llama_sampler_chain_add(sampler_chain, llama_cpp.llama_sampler_init_temp(0.4))
llama_cpp.llama_sampler_chain_add(sampler_chain, llama_cpp.llama_sampler_init_dist(1234))
```

---

## 关键参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| `n_ctx` | int | 上下文窗口大小 (token 数) |
| `n_gpu_layers` | int | GPU 加速层数，-1 表示全部 |
| `n_threads` | int | CPU 线程数 |
| `n_batch` | int | 批处理大小 |
| `temperature` | float | 采样温度 (0.1-1.0) |
| `top_p` | float | Nucleus 采样概率 |
| `top_k` | int | Top-k 采样 |
| `repeat_penalty` | float | 重复惩罚 |
| `chat_format` | str | 聊天格式 (chatml/llama-2 等) |
| `embedding` | bool | 启用嵌入模式 |

---

## 上下文窗口限制

**重要**: `system_tokens + user_tokens + max_tokens` 不能超过模型的 `n_ctx`，否则会导致 segfault。

```python
# 计算上下文使用
n_ctx = 2048
used_tokens = llm.n_tokens(system_prompt) + llm.n_tokens(user_input) + max_tokens
if used_tokens > n_ctx:
    raise ValueError(f"Context overflow: {used_tokens} > {n_ctx}")
```

---

## 并发限制

**重要**: 同一 `Llama` 实例不能并发调用，需串行执行或创建多个实例。

```python
# 错误：并发调用
async def wrong_way():
    results = await asyncio.gather(
        llm("prompt1"),
        llm("prompt2")  # 可能导致竞争条件
    )

# 正确：串行或使用不同实例
async def correct_way():
    results = []
    for prompt in ["prompt1", "prompt2"]:
        results.append(await llm(prompt))
```

---

## 与 FastAPI 集成

```python
from fastapi import FastAPI
from llama_cpp import Llama

app = FastAPI()
llm = None

@app.on_event("startup")
async def load_model():
    global llm
    llm = Llama(
        model_path="./models/llama-model.gguf",
        n_ctx=2048,
        n_threads=8
    )

@app.post("/chat")
async def chat_completion(prompt: str, max_tokens: int = 256):
    response = llm(
        prompt,
        max_tokens=max_tokens,
        temperature=0.7,
        stream=False
    )
    return {"content": response["choices"][0]["text"]}
```

---

## 参考链接

- [llama-cpp-python GitHub](https://github.com/abetlen/llama-cpp-python)
- [官方文档](https://abetlen.github.io/llama-cpp-python/)
- [llama.cpp 核心库](https://github.com/ggerganov/llama.cpp)
