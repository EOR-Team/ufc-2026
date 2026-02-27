#!/bin/bash
# 05_tts_and_assets.sh - 阶段5：TTS、字典资源与依赖防灾核对

source "$(dirname "${BASH_SOURCE[0]}")/00_env.sh"
check_venv

VENV_PYTHON=$(get_python_cmd)

print_section "阶段 5/5: 语音合成引擎及资源部署"

# ==========================================
# 1. 安装 MeloTTS
# ==========================================
print_section "[5.1] 安装 MeloTTS"
WHL_FILE=$(find "$BACKEND_DIR" -maxdepth 1 -name "melotts*.whl" -o -name "melo*.whl" 2>/dev/null | head -n 1)

if [ -n "$WHL_FILE" ]; then
    print_success "找到本地安装包: $WHL_FILE"
    "$VENV_PYTHON" -m pip install "$WHL_FILE"
else
    print_warning "未找到本地 MeloTTS whl 文件，尝试从 GitHub 在线安装..."
    "$VENV_PYTHON" -m pip install "git+https://github.com/myshell-ai/MeloTTS.git"
fi

print_success "MeloTTS 安装步骤结束。"

# ==========================================
# 2. 灾后重建：修复被 MeloTTS 强行降级的 Numpy
# ==========================================
print_section "[5.2] Numpy 依存性灾难修复"
print_warning "MeloTTS 极其顽固的陈旧依赖会将 Numpy 偷偷降级至 1.2x，导致我们的 OpenCV 崩溃。"
print_warning "现在我们将强制把它抢救回 Numpy >= 2。"

"$VENV_PYTHON" -m pip install "numpy>=2" --upgrade

print_success "Numpy 从被降级状态修复成功。"

# ==========================================
# 3. 配置 unidic_lite (MeloTTS 日文分词/中文关联依赖)
# ==========================================
print_section "[5.3] 配置 MeCab 词典软链接"

"$VENV_PYTHON" - <<'EOF'
import sys, os
try:
    import unidic_lite
    import unidic

    lite_dir = unidic_lite.DICDIR
    uni_dir  = unidic.DICDIR

    if not os.path.isfile(os.path.join(uni_dir, "mecabrc")):
        if os.path.exists(uni_dir):
            if os.path.isdir(uni_dir) and not os.path.islink(uni_dir):
                import shutil
                shutil.rmtree(uni_dir)
            else:
                os.remove(uni_dir)
        os.symlink(lite_dir, uni_dir)
        print("\033[0;32m[✓]\033[0m 已成功将 unidic 软链接指向 unidic_lite。避免了联网下载 500MB 全语料字典的痛苦。")
    else:
        print("\033[0;32m[✓]\033[0m unidic 已就绪，无需补链。")
except ImportError:
    print("\033[0;31m[✗]\033[0m 找不到 unidic 模块，可能 MeloTTS 安装存在异常。")
    sys.exit(1)
EOF

# ==========================================
# 4. 下载 NLP 前置资源 (NLTK tagger)
# ==========================================
print_section "[5.4] 预加载 NLTK NLP 标签库"

"$VENV_PYTHON" - <<'EOF'
import nltk, os, sys
download_dir = os.path.join(os.path.dirname(sys.executable), "..", "nltk_data")
abs_dir = os.path.abspath(download_dir)
print(f"正在下载 nltk tagger 到: {abs_dir} ...")
try:
    nltk.download("averaged_perceptron_tagger_eng", download_dir=abs_dir)
    print("\033[0;32m[✓]\033[0m NLTK 资源预载成功。")
except Exception as e:
    print(f"\033[0;31m[!] NLTK 下载失败: {e}\033[0m")
    sys.exit(1)
EOF

# ==========================================
# 5. 处理 STT 模型压缩包 (sherpa-onnx)
# ==========================================
print_section "[5.5] 解压语音识别 STT 模型"

MODEL_DIR="$BACKEND_DIR/src/voice_interaction/models/sherpa-onnx-streaming-paraformer-bilingual-zh-en"
MODEL_TAR=$(find "$BACKEND_DIR" -maxdepth 2 -name "sherpa-onnx-streaming-paraformer-bilingual-zh-en*.tar.*" 2>/dev/null | head -n 1)

if [ -n "$MODEL_TAR" ] && [ ! -d "$MODEL_DIR" ]; then
    echo "发现随仓附带或预下载的压缩包：$MODEL_TAR，正在解压..."
    mkdir -p "$(dirname "$MODEL_DIR")"
    tar -xjf "$MODEL_TAR" -C "$(dirname "$MODEL_DIR")"
    print_success "本地 STT 模型解包完成。"
elif [ -d "$MODEL_DIR" ]; then
    print_success "STT 模型目录已存在：$MODEL_DIR"
else
    print_warning "未找到 STT 模型的本地归档包。"
    print_warning "STT 功能在缺少模型时会引发崩溃。您可以：\n 1. 从项目 Release 手动下载\n 2. 执行 wget https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-streaming-paraformer-bilingual-zh-en.tar.bz2 后放置于 backend 根目录，重新运行此脚本。"
fi

# ==========================================
# 6. 最终的 Import 健壮性测试
# ==========================================
print_section "[5.6] 最终依赖健壮性探针检查"

"$VENV_PYTHON" - <<'EOF'
import sys
modules = [
    ("fastapi",          "FastAPI (Web服务器)"),
    ("llama_cpp",        "llama-cpp-python (大模型推理引擎)"),
    ("openai",           "OpenAI SDK"),
    ("sherpa_onnx",      "sherpa-onnx (语音识别)"),
    ("soundfile",        "soundfile (音频处理)"),
    ("cv2",              "opencv-python (图像处理)"),
    ("face_recognition", "face_recognition (人脸分析引擎)"),
    ("numpy",            "numpy (高性能矩阵)"),
    ("melo",             "MeloTTS (语音合成)"),
]

all_passed = True
for mod, name in modules:
    try:
        __import__(mod)
        print(f"\033[0;32m  [✓]\033[0m {name} 测试加载通过")
    except ImportError as e:
        print(f"\033[0;31m  [✗] {name} 加载异常:\033[0m {e}")
        all_passed = False

if not all_passed:
    print("\n\033[1;33m[!] 发现依赖加载异常，请根据上述提示排查特定的包。你也许只需重新运行失败的该模块对应的脚本。\033[0m")
    sys.exit(1)
EOF

print_success "阶段 5 完成。所有依赖流程结束！"
