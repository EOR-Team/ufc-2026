#!/bin/bash
# install_deps.sh - 一键安装所有后端依赖（Python 3.10.13）

set -e

echo "========================================"
echo "  后端依赖一键安装脚本"
echo "========================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SUCCESS=0
FAILED=0

print_status() {
    if [ "$1" -eq 0 ]; then
        echo -e "${GREEN}[✓]${NC} $2"
        SUCCESS=$((SUCCESS + 1))
    else
        echo -e "${RED}[✗]${NC} $2"
        FAILED=$((FAILED + 1))
    fi
}

print_section() {
    echo ""
    echo -e "${BLUE}>>> $1${NC}"
}

# ========================================
# 1. 检查 Python 3.10
# ========================================
print_section "检查 Python 环境..."

PYTHON_CMD=""
for cmd in python3.10 python3 python; do
    if command -v "$cmd" &> /dev/null; then
        VER=$("$cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null)
        if [ "$VER" = "3.10" ]; then
            PYTHON_CMD="$cmd"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo -e "${RED}[✗] 未找到 Python 3.10，请先安装 Python 3.10.13（推荐通过 pyenv）${NC}"
    echo -e "    pyenv install 3.10.13 && pyenv shell 3.10.13"
    exit 1
fi

PYTHON_VERSION=$("$PYTHON_CMD" --version 2>&1)
PATCH_VER=$("$PYTHON_CMD" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" 2>/dev/null)
if [ "$PATCH_VER" != "3.10.13" ]; then
    echo -e "${YELLOW}[!]${NC} 当前 Python 版本为 $PATCH_VER，推荐使用 3.10.13"
fi
echo -e "${GREEN}[✓]${NC} Python 版本: $PYTHON_VERSION (命令: $PYTHON_CMD)"

# ========================================
# 2. 激活虚拟环境（如存在）
# ========================================
print_section "检查虚拟环境..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

if [ -f "$VENV_DIR/bin/python" ]; then
    echo -e "${GREEN}[✓]${NC} 找到虚拟环境: $VENV_DIR"
else
    echo -e "${YELLOW}[!]${NC} 未找到 venv，将创建新的虚拟环境..."
    "$PYTHON_CMD" -m venv "$VENV_DIR"
    print_status $? "虚拟环境创建完成: $VENV_DIR"
fi

# 所有后续 python 指令均直接使用 venv 中的解释器
PYTHON_CMD="$VENV_DIR/bin/python"
echo -e "${GREEN}[✓]${NC} 使用 Python: $PYTHON_CMD"

# 设置 HF_ENDPOINT 环境变量以使用国内镜像（根据指南建议）
export HF_ENDPOINT="https://hf-mirror.com"
echo -e "${GREEN}[✓]${NC} 设置 HF_ENDPOINT=$HF_ENDPOINT (使用国内镜像)"

# 升级 pip
"$PYTHON_CMD" -m pip install --upgrade pip --quiet
echo -e "${GREEN}[✓]${NC} pip 已升级"

# ========================================
# 3. 安装常规依赖（排除 whl 行）
# ========================================
print_section "安装常规依赖（requirements.txt）..."

# 提取 requirements.txt 中非 whl、非注释、非空的行
REQ_FILE="$SCRIPT_DIR/requirements.txt"

if [ ! -f "$REQ_FILE" ]; then
    echo -e "${RED}[✗] 未找到 requirements.txt${NC}"
    exit 1
fi

# 过滤掉 .whl 行、注释行和空行，生成临时 requirements
TMP_REQ=$(mktemp /tmp/req_filtered_XXXXXX.txt)
grep -v '\.whl' "$REQ_FILE" | grep -v '^\s*#' | grep -v '^\s*$' > "$TMP_REQ"

echo "将安装以下包:"
cat "$TMP_REQ" | sed 's/^/  - /'
echo ""

"$PYTHON_CMD" -m pip install -r "$TMP_REQ"
print_status $? "常规依赖安装完成"
rm -f "$TMP_REQ"

# ========================================
# 4. 安装 MeloTTS（whl 包或从 git 安装）
# ========================================
print_section "安装 MeloTTS..."

WHL_FILE=$(find "$SCRIPT_DIR" -maxdepth 1 -name "melotts*.whl" -o -name "melo*.whl" 2>/dev/null | head -n 1)

if [ -n "$WHL_FILE" ]; then
    # 有本地 whl 文件，优先使用
    echo -e "${GREEN}[✓]${NC} 找到安装包: $WHL_FILE"
    "$PYTHON_CMD" -m pip install "$WHL_FILE"
    print_status $? "MeloTTS 安装完成（使用本地 whl 文件）"

    # MeloTTS 的依赖链会把 numpy 降级到 1.26.x，而 opencv 需要 numpy>=2
    # 安装完成后强制升回兼容版本
    echo -e "${YELLOW}[!]${NC} 修复 numpy 版本冲突（MeloTTS 会降级 numpy，opencv 需要 >=2）..."
    "$PYTHON_CMD" -m pip install "numpy>=2" --quiet
    print_status $? "numpy 版本修复完成（>=2，满足 opencv 要求）"
else
    # 没有本地 whl 文件，尝试从 git 安装（根据指南）
    echo -e "${YELLOW}[!]${NC} 未找到本地 MeloTTS whl 文件，尝试从 GitHub 安装..."
    echo -e "${YELLOW}[!]${NC} 注意：从 git 安装可能需要较长时间，且依赖网络连接"

    # 设置 HF_ENDPOINT 环境变量以使用镜像（根据指南建议）
    export HF_ENDPOINT="https://hf-mirror.com"

    "$PYTHON_CMD" -m pip install "git+https://github.com/myshell-ai/MeloTTS.git"
    if [ $? -eq 0 ]; then
        print_status 0 "MeloTTS 安装完成（从 GitHub 安装）"

        # 同样需要修复 numpy 版本冲突
        echo -e "${YELLOW}[!]${NC} 修复 numpy 版本冲突（MeloTTS 会降级 numpy，opencv 需要 >=2）..."
        "$PYTHON_CMD" -m pip install "numpy>=2" --quiet
        print_status $? "numpy 版本修复完成（>=2，满足 opencv 要求）"
    else
        echo -e "${RED}[✗]${NC} MeloTTS 安装失败，TTS 功能可能不可用"
        echo -e "    请手动安装 MeloTTS："
        echo -e "    1. 下载 melotts*.whl 文件到 backend/ 目录"
        echo -e "    2. 或运行: pip install git+https://github.com/myshell-ai/MeloTTS.git"
        FAILED=$((FAILED + 1))
    fi
fi

# ========================================
# 5. 检查 unidic 字典（MeloTTS 依赖）
# ========================================
print_section "检查 unidic 字典..."

DICT_FILE=$(find "$SCRIPT_DIR" -maxdepth 1 -name "unidic*.zip" 2>/dev/null | head -n 1)

if [ -n "$DICT_FILE" ]; then
    # 有本地压缩包则解压安装完整版
    echo -e "${GREEN}[✓]${NC} 找到本地字典: $DICT_FILE"
    UNIDIC_PATH=$("$PYTHON_CMD" -c "import unidic; print(unidic.DICDIR)" 2>/dev/null || echo "")
    if [ -n "$UNIDIC_PATH" ]; then
        mkdir -p "$UNIDIC_PATH"
        unzip -o -q "$DICT_FILE" -d "$UNIDIC_PATH"
        print_status $? "本地 unidic 字典安装完成"
    else
        echo -e "${YELLOW}[!]${NC} 无法获取字典路径，跳过完整版安装"
    fi
elif "$PYTHON_CMD" -c "import unidic_lite" 2>/dev/null; then
    # MeloTTS 已附带安装 unidic_lite，对中文 TTS 完全够用，无需联网下载
    # 但 MeCab 启动时会查找 unidic 的 dicdir，需将其软链接到 unidic_lite 的字典目录
    UNIDIC_LITE_DIR=$("$PYTHON_CMD" -c "import unidic_lite; print(unidic_lite.DICDIR)" 2>/dev/null || echo "")
    UNIDIC_DIR=$("$PYTHON_CMD" -c "import unidic; print(unidic.DICDIR)" 2>/dev/null || echo "")
    if [ -n "$UNIDIC_LITE_DIR" ] && [ -n "$UNIDIC_DIR" ]; then
        if [ ! -f "$UNIDIC_DIR/mecabrc" ]; then
            echo -e "${YELLOW}[!]${NC} unidic dicdir 为空，软链接到 unidic_lite 字典..."
            rm -rf "$UNIDIC_DIR"
            ln -sf "$UNIDIC_LITE_DIR" "$UNIDIC_DIR"
            print_status $? "unidic_lite -> unidic 软链接创建完成"
        else
            print_status 0 "unidic_lite 已就绪（中文 TTS 可用，无需下载完整 unidic）"
        fi
    else
        echo -e "${YELLOW}[!]${NC} 无法获取字典路径，跳过软链接"
    fi
else
    # 兜底：尝试联网下载完整版，失败仅警告不中断
    echo -e "${YELLOW}[!]${NC} 未找到本地字典，尝试在线下载 unidic（约 500MB）..."
    if "$PYTHON_CMD" -m unidic download; then
        print_status 0 "unidic 在线下载完成"
    else
        echo -e "${YELLOW}[!]${NC} unidic 下载失败（网络问题），中文 TTS 仍可通过 unidic_lite 运行"
    fi
fi

# ========================================
# 6. 验证关键模块
# ========================================
print_section "验证安装结果..."

verify_import() {
    local module="$1"
    local label="$2"
    if "$PYTHON_CMD" -c "import $module" 2>/dev/null; then
        print_status 0 "$label"
    else
        print_status 1 "$label (import $module 失败)"
    fi
}

verify_import "fastapi"          "fastapi"
verify_import "llama_cpp"        "llama-cpp-python"
verify_import "openai"           "openai"
verify_import "dotenv"           "python-dotenv"
verify_import "pydantic"         "pydantic"
verify_import "sherpa_onnx"      "sherpa-onnx"
verify_import "soundfile"        "soundfile"
verify_import "cv2"              "opencv-python"
verify_import "face_recognition" "face_recognition"
verify_import "numpy"            "numpy"

# ---- PyTorch 生态 ----
verify_import "torch"            "torch (PyTorch)"
verify_import "torchaudio"       "torchaudio"
verify_import "transformers"     "transformers (HuggingFace)"
verify_import "librosa"          "librosa"
verify_import "huggingface_hub"  "huggingface_hub"

# PyTorch 功能测试：张量运算 + 设备信息
echo ""
echo "测试 PyTorch 功能..."
TORCH_TEST=$("$PYTHON_CMD" -c "
import warnings
warnings.filterwarnings('ignore')
import torch

# 基本张量运算
a = torch.tensor([1.0, 2.0, 3.0])
b = torch.tensor([4.0, 5.0, 6.0])
c = a + b
assert c.tolist() == [5.0, 7.0, 9.0], 'tensor add failed'

# 矩阵乘法
m = torch.ones(3, 3)
n = torch.eye(3)
r = torch.mm(m, n)
assert r.shape == (3, 3), 'matmul failed'

# 设备信息
cuda_available = torch.cuda.is_available()
device_info = f'CUDA={cuda_available}'
if cuda_available:
    device_info += f', GPU={torch.cuda.get_device_name(0)}, 显存={torch.cuda.get_device_properties(0).total_memory // 1024 // 1024}MB'
else:
    device_info += ' (CPU-only mode)'

print(f'OK|{torch.__version__}|{device_info}')
" 2>&1) || true

if [[ "$TORCH_TEST" == *"OK|"* ]]; then
    TORCH_VER=$(echo "$TORCH_TEST" | grep -oP 'OK\|\K[^|]+')
    TORCH_DEV=$(echo "$TORCH_TEST" | grep -oP 'OK\|[^|]+\|\K.*')
    print_status 0 "PyTorch 功能测试通过 (v${TORCH_VER})"
    echo -e "    ${GREEN}→ 设备: ${NC}${TORCH_DEV}"
else
    print_status 1 "PyTorch 功能测试失败"
    echo "$TORCH_TEST"
fi

# torchaudio 功能测试：生成并转换音频张量
echo ""
echo "测试 torchaudio 功能..."
TORCHAUDIO_TEST=$("$PYTHON_CMD" -c "
import warnings
warnings.filterwarnings('ignore')
import torch, torchaudio

# 生成 1 秒 16kHz 单声道静音张量，验证 resample
waveform = torch.zeros(1, 16000)
resampled = torchaudio.functional.resample(waveform, orig_freq=16000, new_freq=8000)
assert resampled.shape == (1, 8000), f'resample shape error: {resampled.shape}'
print(f'OK|{torchaudio.__version__}')
" 2>&1) || true

if [[ "$TORCHAUDIO_TEST" == *"OK|"* ]]; then
    TA_VER=$(echo "$TORCHAUDIO_TEST" | grep -oP 'OK\|\K.*')
    print_status 0 "torchaudio 功能测试通过 (v${TA_VER})"
else
    print_status 1 "torchaudio 功能测试失败"
    echo "$TORCHAUDIO_TEST"
fi

# transformers 功能测试：tokenizer 加载（离线，不下载模型）
echo ""
echo "测试 transformers 功能..."
TRANSFORMERS_TEST=$("$PYTHON_CMD" -c "
import warnings
warnings.filterwarnings('ignore')
import transformers

# 仅验证核心类可导入，不触发网络请求
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from transformers import PreTrainedModel, PreTrainedTokenizer
print(f'OK|{transformers.__version__}')
" 2>&1) || true

if [[ "$TRANSFORMERS_TEST" == *"OK|"* ]]; then
    TF_VER=$(echo "$TRANSFORMERS_TEST" | grep -oP 'OK\|\K.*')
    print_status 0 "transformers 功能测试通过 (v${TF_VER})"
else
    print_status 1 "transformers 功能测试失败"
    echo "$TRANSFORMERS_TEST"
fi

# librosa 功能测试：生成信号并提取 MFCC
echo ""
echo "测试 librosa 功能..."
LIBROSA_TEST=$("$PYTHON_CMD" -c "
import warnings
warnings.filterwarnings('ignore')
import numpy as np, librosa

# 生成 0.5 秒 440Hz 正弦波，提取 MFCC
sr = 22050
duration = 0.5
t = np.linspace(0, duration, int(sr * duration))
y = np.sin(2 * np.pi * 440 * t).astype(np.float32)
mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
assert mfcc.shape[0] == 13, f'MFCC shape error: {mfcc.shape}'
print(f'OK|{librosa.__version__}')
" 2>&1) || true

if [[ "$LIBROSA_TEST" == *"OK|"* ]]; then
    LR_VER=$(echo "$LIBROSA_TEST" | grep -oP 'OK\|\K.*')
    print_status 0 "librosa 功能测试通过 (v${LR_VER})"
else
    print_status 1 "librosa 功能测试失败"
    echo "$LIBROSA_TEST"
fi

# huggingface_hub 功能测试：验证缓存目录可访问
echo ""
echo "测试 huggingface_hub 功能..."
HF_TEST=$("$PYTHON_CMD" -c "
import warnings
warnings.filterwarnings('ignore')
import huggingface_hub
from huggingface_hub import constants
cache_dir = constants.HF_HUB_CACHE
print(f'OK|{huggingface_hub.__version__}|{cache_dir}')
" 2>&1) || true

if [[ "$HF_TEST" == *"OK|"* ]]; then
    HF_VER=$(echo "$HF_TEST" | grep -oP 'OK\|\K[^|]+')
    HF_CACHE=$(echo "$HF_TEST" | grep -oP 'OK\|[^|]+\|\K.*')
    print_status 0 "huggingface_hub 功能测试通过 (v${HF_VER})"
    echo -e "    ${GREEN}→ 缓存目录: ${NC}${HF_CACHE}"
else
    print_status 1 "huggingface_hub 功能测试失败"
    echo "$HF_TEST"
fi

# 验证 MeloTTS
echo ""
echo "测试 MeloTTS 模块..."
MELO_OUT="$SCRIPT_DIR/melo_test.wav"
# 用 || true 防止 set -e 在命令替换返回非零时提前终止脚本
MELO_TEST=$("$PYTHON_CMD" -c "
import os, warnings
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
warnings.filterwarnings('ignore')
from melo.api import TTS
tts = TTS(language='ZH', device='cpu')
tts.tts_to_file('测试用音频，跟我念123开始。', speaker_id=0, output_path='$MELO_OUT')
print('OK')
" 2>&1) || true

if [[ "$MELO_TEST" == *"OK"* ]]; then
    print_status 0 "MeloTTS 语音合成测试通过"
    if [ -f "$MELO_OUT" ]; then
        FILE_SIZE=$(stat -c%s "$MELO_OUT" 2>/dev/null || stat -f%z "$MELO_OUT" 2>/dev/null)
        echo -e "    ${GREEN}→ 测试音频已生成：${NC}$MELO_OUT"
        echo -e "    ${GREEN}→ 文件大小：${NC}${FILE_SIZE} bytes"
        echo -e "    ${YELLOW}提示：可用播放器检查后手动删除该文件${NC}"
    fi
else
    print_status 1 "MeloTTS 语音合成测试失败"
    echo "$MELO_TEST"
fi

# ========================================
# 6.1 额外资源：NLTK 资源 & 模型文件
# ========================================
print_section "检查并安装 NLTK 资源与模型文件"

# 指定虚拟环境下的 nltk_data 存放位置，避免与系统冲突
VENV_NLTK_DIR="$VENV_DIR/nltk_data"
mkdir -p "$VENV_NLTK_DIR"

echo "将下载 NLTK 资源：averaged_perceptron_tagger_eng 到 $VENV_NLTK_DIR"
"$PYTHON_CMD" - <<PY
import nltk, os, sys
download_dir = os.path.abspath(os.path.join(os.path.dirname(sys.executable), '..', 'nltk_data'))
try:
    nltk.download('averaged_perceptron_tagger_eng', download_dir=download_dir)
    print('NLTK resource downloaded to', download_dir)
except Exception as e:
    print('NLTK download failed:', e)
    sys.exit(1)
PY
print_status $? "NLTK 资源安装"

# 如果仓库中包含 sherpa 模型压缩包，尝试解压到正确位置
MODEL_TAR=$(find "$SCRIPT_DIR" -maxdepth 2 -name "sherpa-onnx-streaming-paraformer-bilingual-zh-en*.tar.*" 2>/dev/null | head -n 1)
MODEL_DIR="$SCRIPT_DIR/src/voice_interaction/models/sherpa-onnx-streaming-paraformer-bilingual-zh-en"

if [ -n "$MODEL_TAR" ] && [ ! -d "$MODEL_DIR" ]; then
    echo "找到模型压缩包: $MODEL_TAR，正在解压到 $MODEL_DIR"
    mkdir -p "$(dirname "$MODEL_DIR")"
    tar -xjf "$MODEL_TAR" -C "$(dirname "$MODEL_DIR")"
    print_status $? "解压 sherpa 模型包"
elif [ -d "$MODEL_DIR" ]; then
    print_status 0 "sherpa 模型目录已存在"
else
    # 如果本地没有模型，尝试从网络下载（根据指南中的链接）
    echo -e "${YELLOW}[!]${NC} 未找到本地模型，尝试从网络下载 paraformer 中英双语模型..."
    MODEL_URL="https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-streaming-paraformer-bilingual-zh-en.tar.bz2"
    MODEL_TAR_DL="$SCRIPT_DIR/sherpa-onnx-streaming-paraformer-bilingual-zh-en.tar.bz2"

    if command -v wget &> /dev/null; then
        wget -q "$MODEL_URL" -O "$MODEL_TAR_DL"
        if [ $? -eq 0 ] && [ -f "$MODEL_TAR_DL" ]; then
            echo -e "${GREEN}[✓]${NC} 模型下载成功: $MODEL_TAR_DL"
            mkdir -p "$(dirname "$MODEL_DIR")"
            tar -xjf "$MODEL_TAR_DL" -C "$(dirname "$MODEL_DIR")"
            print_status $? "解压下载的 sherpa 模型包"
            rm -f "$MODEL_TAR_DL"
        else
            echo -e "${RED}[✗]${NC} 模型下载失败，STT 可能不可用"
            echo -e "    请手动下载模型并放置在 backend/ 目录下:"
            echo -e "    wget $MODEL_URL"
        fi
    else
        echo -e "${RED}[✗]${NC} 未找到 wget 命令，无法下载模型"
        echo -e "    请手动下载模型并放置在 backend/ 目录下:"
        echo -e "    wget $MODEL_URL"
    fi
fi

# 验证模型文件结构（根据指南中的模型结构说明）
if [ -d "$MODEL_DIR" ]; then
    echo ""
    echo "验证 sherpa-onnx 模型文件结构..."

    REQUIRED_FILES=("encoder.onnx" "decoder.onnx" "tokens.txt")
    MISSING_FILES=()

    for file in "${REQUIRED_FILES[@]}"; do
        if [ ! -f "$MODEL_DIR/$file" ]; then
            MISSING_FILES+=("$file")
        fi
    done

    if [ ${#MISSING_FILES[@]} -eq 0 ]; then
        echo -e "${GREEN}[✓]${NC} 模型文件结构完整"
        echo -e "    ${GREEN}→${NC} 找到: encoder.onnx, decoder.onnx, tokens.txt"

        # 检查可选文件
        OPTIONAL_FILES=("encoder.int8.onnx" "decoder.int8.onnx" "test_wavs/")
        for file in "${OPTIONAL_FILES[@]}"; do
            if [ -e "$MODEL_DIR/$file" ]; then
                echo -e "    ${GREEN}→${NC} 找到可选文件: $file"
            fi
        done
    else
        echo -e "${YELLOW}[!]${NC} 模型文件不完整，缺少: ${MISSING_FILES[*]}"
        echo -e "    请确保模型目录包含以下必需文件:"
        echo -e "    - encoder.onnx"
        echo -e "    - decoder.onnx"
        echo -e "    - tokens.txt"
        echo -e "    模型目录: $MODEL_DIR"
    fi
else
    echo -e "${YELLOW}[!]${NC} 模型目录不存在，跳过模型验证"
fi

# ========================================
# 7. 输出汇总
# ========================================
echo ""
echo "========================================"
echo "  安装结果统计"
echo "========================================"
echo -e "成功: ${GREEN}$SUCCESS${NC}"
echo -e "失败: ${RED}$FAILED${NC}"

if [ "$FAILED" -eq 0 ]; then
    echo ""
    echo -e "${GREEN}>>> 所有依赖安装完成！${NC}"
    echo ""
    echo "激活虚拟环境后启动项目："
    echo "  source venv/bin/activate"
    echo "  uvicorn src.main:app --reload"
    exit 0
else
    echo ""
    echo -e "${RED}>>> 安装过程中存在错误，请检查上述输出${NC}"
    exit 1
fi
