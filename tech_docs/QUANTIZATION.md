# 模型量化指南

## 什么是量化

量化是将大模型的高精度权重（如 FP32/FP16）转换为低精度格式（如 INT8/INT4）的过程，在保持模型能力的同时大幅减少内存占用和计算开销。

---

## 量化级别对比

| 类型 | 位宽 | 压缩率 | 质量损失 | 推荐场景 |
|------|------|--------|----------|----------|
| **FP16** | 16bit | 1x | 无 | 基准参考 |
| **FP32** | 32bit | 2x | 无 | 精度优先 |
| **Q8_0** | 8bit | 4x | 极小 | 高质量需求 |
| **Q6_K** | ~6.6bit | ~5x | 很小 | 平衡选择 |
| **Q5_K_M** | ~5.7bit | ~6x | 小 | 日常使用 |
| **Q4_K_M** | ~4.9bit | ~7x | 中等 | **推荐轻量** |
| **Q4_K_S** | ~4.7bit | ~8x | 中等偏大 | 轻量部署 |
| **Q3_K_M** | ~3.8bit | ~10x | 较大 | 极端轻量 |
| **Q2_K** | ~3.2bit | ~12x | 较大 | 最低资源 |

---

## 树莓派 4B 推荐配置

| RAM | 推荐量化 | 内存占用 | n_ctx |
|-----|----------|----------|-------|
| 4GB | Q4_K_M | ~1.2GB | 2048 |
| 4GB | Q3_K_M | ~1.0GB | 2048 |
| 8GB | Q4_K_M | ~1.2GB | 4096 |

---

## 量化工具

### llama-quantize

```bash
# 基本语法
llama-quantize <input.gguf> <output.gguf> <quant_type>

# FP16 转 Q4_K_M
llama-quantize model-f16.gguf model-q4_k_m.gguf Q4_K_M

# FP16 转 Q5_K_M
llama-quantize model-f16.gguf model-q5_k_m.gguf Q5_K_M

# FP16 转 Q8_0
llama-quantize model-f16.gguf model-q8_0.gguf Q8_0
```

### 使用重要性矩阵 (提升质量)

```bash
# 1. 计算重要性矩阵
./llama-cli -m model-f16.gguf \
            --save-imatrix imatrix.dat \
            --threads 8

# 2. 使用重要性矩阵量化
llama-quantize --imatrix imatrix.dat \
                model-f16.gguf \
                model-q4_k_m.gguf \
                Q4_K_M
```

---

## LFM2.5-1.2B 量化示例

### 下载 FP16 版本

```bash
# 从 Ollama 导出
ollama pull lfm2.5:1.2b
# 使用 ollama-tools 导出为 GGUF

# 或从 HF 下载 (如果有)
```

### 量化步骤

```bash
# 1. 确认模型已转为 GGUF FP16
ls -lh lfm2.5-1.2b-f16.gguf

# 2. 量化到 Q4_K_M (推荐)
llama-quantize lfm2.5-1.2b-f16.gguf \
                lfm2.5-1.2b-q4_k_m.gguf \
                Q4_K_M

# 3. 验证大小
ls -lh lfm2.5-1.2b*.gguf
```

### 验证量化质量

```python
from llama_cpp import Llama

# 加载原版和量化版
f16_model = Llama("lfm2.5-1.2b-f16.gguf", n_ctx=512, verbose=False)
q4_model = Llama("lfm2.5-1.2b-q4_k_m.gguf", n_ctx=512, verbose=False)

test_prompts = [
    "解释什么是人工智能",
    "1+1等于几",
    "写一首关于春天的诗"
]

for prompt in test_prompts:
    f16_out = f16_model(prompt, max_tokens=50)["choices"][0]["text"]
    q4_out = q4_model(prompt, max_tokens=50)["choices"][0]["text"]

    print(f"Prompt: {prompt}")
    print(f"FP16: {f16_out[:100]}...")
    print(f"Q4:   {q4_out[:100]}...")
    print("---")
```

---

## 量化类型详解

### Q4_K_M (推荐)

```
特点:
- 4-bit 量化，每权重 4.9 bits
- K-means 聚类 + 量化
- 质量与 FP16 相近
- 压缩率 ~7x

适用: 大多数场景的首选
```

### Q5_K_M

```
特点:
- 5-bit 量化，每权重 5.7 bits
- 比 Q4_K_M 更好的质量
- 压缩率 ~6x

适用: 质量敏感场景
```

### Q3_K_M

```
特点:
- 3-bit 量化，每权重 3.8 bits
- 更激进的压缩
- 轻微质量下降

适用: 内存极度受限
```

---

## 批量量化脚本

```bash
#!/bin/bash
# quantize-all.sh

MODEL="lfm2.5-1.2b"
INPUT="${MODEL}-f16.gguf"

# 量化级别数组
QUANTS=("Q4_K_M" "Q5_K_M" "Q6_K" "Q8_0")

for Q in "${QUANTS[@]}"; do
    OUTPUT="${MODEL}-${Q,,}.gguf"
    echo "Quantizing to $Q..."
    llama-quantize "$INPUT" "$OUTPUT" "$Q"
    echo "Done: $OUTPUT"
    ls -lh "$OUTPUT"
done
```

运行:
```bash
chmod +x quantize-all.sh
./quantize-all.sh
```

---

## 常见问题

### Q: 量化后模型质量下降明显吗？

**A**: Q4_K_M 级别通常质量损失很小（<5%），对于大多数任务不可察觉。Q3_K_M 以下可能会有明显下降。

### Q: 如何选择量化级别？

**A**: 
- 内存充足 → Q5_K_M 或 Q6_K
- 内存有限 → Q4_K_M (推荐)
- 极端受限 → Q3_K_M

### Q: 可以量化已经量化过的模型吗？

**A**: 不建议，应该从 FP16/F32 开始量化。

### Q: 量化后可以反向转换吗？

**A**: 不能，量化是单向的。

---

## 性能基准

### 推理速度 (LFM2.5-1.2B, AMD Ryzen 5)

| 量化 | tokens/s | 相对速度 |
|------|----------|----------|
| FP16 | ~80 | 1.0x |
| Q8_0 | ~150 | 1.9x |
| Q6_K | ~180 | 2.3x |
| Q5_K_M | ~210 | 2.6x |
| Q4_K_M | ~239 | 3.0x |
| Q3_K_M | ~280 | 3.5x |

### 内存占用 (LFM2.5-1.2B)

| 量化 | 模型大小 | 运行时 RAM |
|------|----------|------------|
| FP16 | ~2.4GB | ~2.8GB |
| Q8_0 | ~1.2GB | ~1.6GB |
| Q6_K | ~0.9GB | ~1.3GB |
| Q5_K_M | ~0.8GB | ~1.2GB |
| Q4_K_M | ~0.7GB | ~1.0GB |
| Q3_K_M | ~0.5GB | ~0.8GB |
