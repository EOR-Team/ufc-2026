# LFM2.5-1.2B-Instruct 模型指南

## 概述

LFM2.5-1.2B (Large Foundation Model 2.5) 是 Liquid AI 推出的轻量级文本生成模型，专为边缘设备和资源受限环境优化。1.2B 参数规模使其能够在树莓派、旧款笔记本和移动设备上高效运行。

**特点**:
- 1.2B 参数，轻量高效
- 支持中文和英文
- "Thinking" 版本支持链式推理
- GGUF 格式优化，适合 llama.cpp

---

## 模型规格

| 规格 | 数值 |
|------|------|
| 参数量 | 1.2B (12亿) |
| 上下文窗口 | 2K - 8K (视版本) |
| 量化后大小 | ~700MB (Q4_K_M) |
| 运行时内存 | ~890MB |
| 推理速度 | ~239 tokens/s (AMD CPU) |

---

## Thinking vs 非 Thinking 版本

| 版本 | 特点 | 适用场景 |
|------|------|----------|
| **LFM2.5-1.2B** | 标准文本生成 | 快速响应，简单任务 |
| **LFM2.5-1.2B-Thinking** | 链式推理 (CoT) | 复杂逻辑，数学推导，代码解释 |

---

## 部署方式

### 方式 1: Ollama (最简单)

```bash
# 安装 Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 下载模型
ollama pull lfm2.5:1.2b

# 运行
ollama run lfm2.5:1.2b

# 对话示例
>>> 你好，请介绍一下你自己
我是 LFM2.5，一个轻量级 AI 助手...
```

### 方式 2: llama.cpp (推荐用于嵌入式)

```bash
# 克隆 llama.cpp
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp

# 编译
make -j$(nproc)

# 从 Ollama 导出 GGUF (需要 ollama-tools)
# 或下载现成的 GGUF 模型

# 运行
./llama-cli -m ./models/lfm2.5-1.2b.q4_k_m.gguf \
            -p "你好，介绍一下你自己" \
            -n 256 \
            -t 8
```

### 方式 3: llama-cpp-python

```python
from llama_cpp import Llama

llm = Llama(
    model_path="./models/lfm2.5-1.2b.q4_k_m.gguf",
    n_ctx=2048,
    n_threads=8,
    chat_format="chatml"  # 或 llama-2, 根据模型确定
)

response = llm.create_chat_completion(
    messages=[
        {"role": "user", "content": "你好，请介绍一下你自己"}
    ],
    max_tokens=256,
    temperature=0.7
)

print(response["choices"][0]["message"]["content"])
```

### 方式 4: API 服务器

```bash
# 安装并启动服务器
pip install 'llama-cpp-python[server]'

python3 -m llama_cpp.server \
    --model ./models/lfm2.5-1.2b.q4_k_m.gguf \
    --chat_format chatml \
    --port 8000
```

客户端调用:
```python
import openai

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="not-needed"
)

response = client.chat.completions.create(
    model="lfm2.5",
    messages=[{"role": "user", "content": "解释什么是量子计算"}],
    temperature=0.7
)
print(response.choices[0].message.content)
```

---

## GGUF 模型下载

### 官方渠道

```bash
# Ollama (自动管理)
ollama pull lfm2.5:1.2b

# Hugging Face (如果有)
# 搜索: lfm2.5-1.2b-instruct gguf
```

### 社区镜像

```bash
# 国内镜像加速
export HF_ENDPOINT=https://hf-mirror.com

huggingface-cli download \
  --local-dir ./models \
  liquid-lfm/LFM2.5-1.2B-Instruct-GGUF \
  lfm2.5-1.2b-instruct.Q4_K_M.gguf
```

---

## 性能基准

### CPU 推理 (AMD Ryzen 5 5600H)

| 量化级别 | 速度 | 内存占用 |
|----------|------|----------|
| Q8_0 | ~150 tokens/s | ~1.8GB |
| Q6_K | ~180 tokens/s | ~1.4GB |
| Q4_K_M | ~239 tokens/s | ~890MB |
| Q3_K_M | ~280 tokens/s | ~700MB |

### 设备兼容性

| 设备 | 量化 | 可行性 |
|------|------|--------|
| 树莓派 4B 4GB | Q4_K_M | ✅ 推荐 |
| 树莓派 4B 8GB | Q4_K_M | ✅ 流畅 |
| Android 手机 | Q3_K_M | ✅ 可行 |
| MacBook Air M2 | Q4_K_M | ✅ 流畅 |
| MacBook Air M1 | Q4_K_M | ✅ 流畅 |

---

## 医疗问答场景应用

### 系统提示词设计

```python
SYSTEM_PROMPT = """你是一个智能医疗分诊助手。请根据用户的症状描述，提供以下信息：
1. 可能的相关科室
2. 症状的紧急程度评估
3. 建议的下一步行动

注意：你的建议仅供参考，不能替代专业医疗诊断。"""

messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": "我已经头痛三天了，还有点发烧，应该怎么办？"}
]

response = llm.create_chat_completion(
    messages=messages,
    max_tokens=512,
    temperature=0.3  # 医疗场景用较低温度
)
```

### 上下文管理

```python
# 跟踪对话历史，控制 token 使用
def build_medical_context(history: list, max_turns: int = 5) -> list:
    """保留最近 N 轮对话"""
    return history[-max_turns:] if len(history) > max_turns else history

# 检查上下文长度
total_tokens = sum(llm.n_tokens(str(msg)) for msg in context)
if total_tokens > 1800:  # 留空间给生成
    # 压缩或截断早期消息
    context = compress_context(context)
```

---

## 常见问题

### Q: LFM2.5 支持中文吗？

**A**: 是的，Instruct 版本支持中文和英文。

### Q: 需要多大的内存？

**A**: Q4_K_M 量化版本运行时约 890MB，加上 llama.cpp 开销，建议 2GB+ 可用内存。

### Q: 如何选择 Thinking vs 非 Thinking？

**A**:
- 简单问答、文本生成 → 非 Thinking (更快)
- 数学推导、代码解释、复杂推理 → Thinking (更准确)

### Q: 如何量化自定义版本？

```bash
# 使用 llama-quantize
llama-quantize lfm2.5-1.2b-f16.gguf \
                lfm2.5-1.2b-q4_k_m.gguf \
                Q4_K_M
```

---

## 参考资源

### 官方资源

- [LFM 模型介绍](https://liquidai.ai/)
- [Ollama LFM2.5](https://ollama.com/library/lfm2.5)

### 社区教程

- [CSDN: LFM2.5-1.2B 部署教程](https://blog.csdn.net/)
- [Ollama 一键部署教程](https://blog.csdn.net/)

### 模型下载

- [Ollama Library](https://ollama.com/library/lfm2.5)
- [Hugging Face (搜索 lfm2.5 gguf)](https://huggingface.co/models)

---

## 总结

LFM2.5-1.2B-Instruct 是嵌入式和边缘设备推理的理想选择：

| 优势 | 说明 |
|------|------|
| ✅ 轻量高效 | 1.2B 参数，Q4_K_M 仅 ~700MB |
| ✅ 跨平台 | 支持 llama.cpp 所有后端 |
| ✅ 中文支持 | 完整的中英文推理能力 |
| ✅ 医疗适配 | 可通过提示词工程优化医疗场景 |

**推荐配置 (树莓派 4B)**:
- 模型量化: Q4_K_M
- n_ctx: 2048
- n_threads: 4 (4GB RAM) 或 8 (8GB RAM)
