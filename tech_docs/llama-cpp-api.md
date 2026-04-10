# llama-cpp API 参考

## 概述

llama-cpp-python 提供两种 API 层级：
1. **高层 API**: `Llama` 类，简单易用
2. **低层 API**: 直接调用 CFFI 函数

---

## Llama 类 (高层 API)

### 初始化参数

```python
from llama_cpp import Llama

llm = Llama(
    model_path: str,              # GGUF 模型路径 (必需)
    n_ctx: int = 2048,           # 上下文窗口大小
    n_parts: int = -1,            # 模型分片数 (-1=自动)
    n_gpu_layers: int = 0,        # GPU 加速层数
    n_threads: int = 4,           # CPU 线程数
    n_threads_batch: int = None,  # 批处理线程数
    n_batch: int = 512,           # 批处理大小
    rope_scaling_type: int = None,# RoPE 缩放类型
    rope_freq_base: float = 0,    # RoPE 频率基址
    rope_freq_scale: float = 0,   # RoPE 频率缩放
    yarn_attn_factor: float = 1,   # YaRN 注意力因子
    yarn_beta_fast: float = 32,   # YaRN beta_fast
    yarn_beta_slow: float = 1,    # YaRN beta_slow
    yarn_orig_ctx: int = 0,       # YaRN 原始上下文
    use_mmap: bool = True,        # 内存映射
    use_mlock: bool = False,      # 内存锁定
    embedding: bool = False,       # 嵌入模式
    chat_format: str = None,      # 聊天格式
    chat_handler: str = None,     # 聊天处理器
    verbose: bool = True,         # 详细输出
)
```

### 主要方法

#### `__call__(prompt, ...)` - 文本补全

```python
response = llm(
    prompt: str,                  # 输入提示词
    max_tokens: int = 256,        # 最大生成 token 数
    temperature: float = 0.8,     # 采样温度
    top_p: float = 0.95,          # Nucleus 采样
    top_k: int = 40,             # Top-k 采样
    repeat_penalty: float = 1.1, # 重复惩罚
    stop: list = [],              # 停止词列表
    stream: bool = False,         # 流式输出
    tfs_z: float = 1,             # Tail-free 采样
    mirostat_mode: int = 0,       # Mirostat 模式
    mirostat_tau: float = 5,     # Mirostat tau
    mirostat_eta: float = 0.1,   # Mirostat eta
)
```

**返回值**:
```python
{
    "choices": [
        {
            "text": "生成的文本",
            "index": 0,
            "logprobs": {...},
            "finish_reason": "stop"
        }
    ],
    "usage": {
        "prompt_tokens": 10,
        "completion_tokens": 50,
        "total_tokens": 60
    }
}
```

#### `create_chat_completion(messages, ...)` - 聊天补全

```python
response = llm.create_chat_completion(
    messages: list,               # 消息列表
    max_tokens: int = 256,        # 最大 token 数
    temperature: float = 0.8,     # 采样温度
    top_p: float = 0.95,          # Nucleus 采样
    top_k: int = 40,             # Top-k 采样
    repeat_penalty: float = 1.1, # 重复惩罚
    stop: list = [],              # 停止词
    stream: bool = False,         # 流式输出
    response_format: dict = None, # 响应格式 (如 {"type": "json_object"})
    tools: list = None,          # 工具定义
    tool_choice: str = None,      # 工具选择
)
```

**消息格式**:
```python
messages = [
    {"role": "system", "content": "系统提示词"},
    {"role": "user", "content": "用户消息"},
    {"role": "assistant", "content": "助手回复"},
    {"role": "user", "content": "Follow-up question"}
]
```

**返回值**:
```python
{
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "助手的回复内容"
            },
            "finish_reason": "stop"
        }
    ],
    "usage": {
        "prompt_tokens": 50,
        "completion_tokens": 100,
        "total_tokens": 150
    }
}
```

#### 流式响应处理

```python
# 文本补全流式
stream = llm("Write a story:", stream=True)
for chunk in stream:
    if "choices" in chunk and len(chunk["choices"]) > 0:
        print(chunk["choices"][0]["text"], end="", flush=True)

# 聊天补全流式
stream = llm.create_chat_completion(
    messages=[{"role": "user", "content": "Hello!"}],
    stream=True
)
for chunk in stream:
    delta = chunk["choices"][0]["delta"]
    if "content" in delta:
        print(delta["content"], end="", flush=True)
```

### 属性

```python
# Token 计数
n_tokens = llm.n_tokens("some text")  # 返回 token 数

# 模型信息
model_path = llm.model_path
n_ctx = llm.n_ctx()                    # 上下文大小
```

---

## 低层 CFFI API

### 核心结构体

```python
import llama_cpp as llama_cpp

# 模型参数
model_params = llama_cpp.llama_model_default_params()
model_params.n_gpu_layers = 35  # GPU 层数

# 上下文参数
ctx_params = llama_cpp.llama_context_default_params()
ctx_params.n_ctx = 4096         # 上下文大小
ctx_params.n_batch = 512        # 批处理大小
```

### 采样器链

```python
# 创建采样器链
sampler_chain = llama_cpp.llama_sampler_chain_from_params(
    llama_cpp.llama_sampler_chain_default_params()
)

# 添加采样器
llama_cpp.llama_sampler_chain_add(sampler_chain, llama_cpp.llama_sampler_init_temp(0.7))
llama_cpp.llama_sampler_chain_add(sampler_chain, llama_cpp.llama_sampler_init_top_k(40))
llama_cpp.llama_sampler_chain_add(sampler_chain, llama_cpp.llama_sampler_init_top_p(0.95))
llama_cpp.llama_sampler_chain_add(sampler_chain, llama_cpp.llama_sampler_init_repetition_penalty(1.1))

# 采样
new_token = llama_cpp.llama_sampler_sample(sampler_chain, ctx, -1)

# 清理
llama_cpp.llama_sampler_free(sampler_chain)
```

### Token 处理

```python
# 获取词汇表大小
n_vocab = llama_cpp.llama_n_vocab(model)

# 检查 EOS token
is_eos = llama_cpp.llama_token_is_eog(model, token)

# 转换 token 为文本
buf = (ctypes.c_char * 32)()
outlen = llama_cpp.llama_token_to_piece(model, token, buf, len(buf), 0, False)
text = bytes(buf[:outlen]).decode("utf-8")

# 转换文本为 tokens
tokens = llama_cpp.llama_tokenize(model, text.encode("utf-8"), False)
```

---

## LlamaCache 类 (KV Cache 管理)

```python
from llama_cpp import Llama, LlamaCache

# 创建缓存
cache = LlamaCache()
cache.ctx = ctx  # 关联上下文

# 使用缓存
llm = Llama(model_path="./model.gguf", cache=cache)

# 缓存命中时会加速
response1 = llm("Hello")   # 首次生成
response2 = llm("Hello")   # 使用缓存，加速
```

---

## LlamaBatch 类 (批处理)

```python
from llama_cpp import LlamaBatch

batch = LlamaBatch(
    n_tokens=512,      # 最大 token 数
    n_seq_max=8,       # 最大序列数
)

# 添加 token
batch.add_token(token_id=123, pos=0, seq_id=0, logits=True)
batch.add_token(token_id=456, pos=1, seq_id=0, logits=True)

# 解码
llama_cpp.llama_decode(ctx, batch)

# 获取 logits
logits = llama_cpp.llama_get_logits(ctx)
```

---

## 错误处理

```python
try:
    llm = Llama(model_path="./model.gguf")
except Exception as e:
    print(f"Failed to load model: {e}")

# 检查上下文溢出
if total_tokens > llm.n_ctx():
    raise ValueError("Context overflow - reduce prompt or increase n_ctx")
```

---

## 完整示例

```python
from llama_cpp import Llama

# 初始化
llm = Llama(
    model_path="./models/lfm2.5-1.2b.q4_k_m.gguf",
    n_ctx=2048,
    n_threads=8,
    n_gpu_layers=0,  # 树莓派无 GPU
    verbose=False
)

# 聊天补全
messages = [
    {"role": "system", "content": "你是一个医疗分诊助手。"},
    {"role": "user", "content": "我头痛三天了，应该挂什么科？"}
]

response = llm.create_chat_completion(
    messages=messages,
    max_tokens=256,
    temperature=0.3,
    stop=["用户:", "Assistant:"]
)

print(response["choices"][0]["message"]["content"])

# Token 使用统计
print(f"使用 tokens: {response['usage']['total_tokens']}")
```
