# ARM64 (树莓派) 依赖安装脚本重构计划

## 1. 目标
将原先庞大且脆弱的 `install_deps.sh` 拆分为模块化、分层、容错的多个脚本存放于 `backend/installation/`，特别针对类似树莓派 4B/5 等 aarch64 设备的资源受限、编译耗时、依赖冲突等问题（OOM、numpy 降级、dlib 编译）进行专项处理。

## 2. 目录结构设计
```text
backend/
├── installation/
│   ├── install_all.sh             # 总控入口，顺序执行以下全部
│   ├── 00_env.sh                  # 环境检测与公共函数库（被 source）
│   ├── 01_system_deps.sh          # Apt 级依赖（OpenBLAS、CMake、构建工具）
│   ├── 02_core_ai_frameworks.sh   # 核心 AI 框架（PyTorch、OpenCV-headless、Dlib 编译治 OOM）
│   ├── 03_llama_engine.sh         # Llama-cpp 编译（强制 OpenBLAS 链接）
│   ├── 04_general_deps.sh         # 常规纯 Python 包（FastAPI 等）
│   └── 05_tts_and_assets.sh       # MeloTTS 安装、numpy 版本修正、字典软链接、资源预载
```

## 3. 核心痛点与对策 (ARM64 特供)

### 痛点 A：Dlib 编译导致的 OOM 杀进程
**对策**：在 `02_core_ai_frameworks.sh` 中检测可用内存（物理 RAM + Swap），若总可用内存小于 4GB，临时创建一个 4GB 的 Swap 文件并在编译结束后删除。

### 痛点 B：Numpy 版本地狱
**对策**：
1. `02` 安装 OpenCV 时强制 `numpy>=2` 且使用 `opencv-python-headless` (避免 ARM 上的 GUI Qt 依赖地狱)。
2. `05` 安装 MeloTTS 时，它自带极其顽固的陈旧依赖树会将 `numpy` 降级到 `1.26.x`。
3. **关键操作**：在 `05` 的结尾，强制执行 `pip install "numpy>=2" --upgrade` 将版本拉回现代，否则 `cv2` 会在运行时直接 dumped core。

### 痛点 C：PyTorch 在 ARM 上的包寻找
**对策**：不依赖系统源，在 `02` 中显式指定 `--index-url https://download.pytorch.org/whl/cpu`，让 pip 拉取官方针对 aarch64 的预编译 CPU wheel，避免几十个小时的源码编译。

### 痛点 D：Llama.cpp 的硬件加速
**对策**：在 `01` 中确保 `libopenblas-dev` 存在，在 `03` 安装时注入 `CMAKE_ARGS="-DGGML_BLAS=ON -DGGML_BLAS_VENDOR=OpenBLAS"` 并强制 `--no-binary llama-cpp-python`，确保生成带加速的 `.so` 动态库。

## 4. 依赖项重定向矩阵
在拆分 `requirements.txt` 时，各个包的分发如下：

- **02 脚本承接**: `numpy`, `opencv-python-headless`, `face_recognition` (带出 dlib), `torch`, `torchaudio`
- **03 脚本承接**: `llama-cpp-python[all]`
- **05 脚本承接**: `melotts-0.1.2-py3-none-any.whl` (或 git), `sherpa-onnx`
- **04 脚本承接**: 原 `requirements.txt` 中剔除上述包及其空行/注释后的**所有剩余项** (`fastapi`, `openai`, `pydantic` 等)。

## 5. 部署路径
1. 创建 `backend/installation/` 文件夹。
2. 依次生成六个 shell 脚本并赋予 `chmod +x`。
3. 验证通过后（不抛出语法错误），将旧的 `install_deps.sh` 标记为废弃（也可重命名为 `install_deps.old.sh` 或更新说明中提及迁移向导）。

---
*注：此文件由系统自我生成，作为架构蓝图与进度核对清单。*