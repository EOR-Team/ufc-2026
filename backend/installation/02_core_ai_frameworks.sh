#!/bin/bash
# 02_core_ai_frameworks.sh - 阶段2：核心 AI 框架解决与防 OOM 处理

source "$(dirname "${BASH_SOURCE[0]}")/00_env.sh"
check_venv

VENV_PYTHON=$(get_python_cmd)
ARCH=$(uname -m)

print_section "阶段 2/5: 安装核心 AI 框架 (Torch, OpenCV, Dlib)"

# ==========================================
# 1. 解决 PyTorch 依赖
# ==========================================
print_section "安装 PyTorch 家族..."

if [ "$ARCH" = "aarch64" ]; then
    print_warning "在 aarch64 上强制从官方下载编译好的 CPU 版本 Wheel，避免几十小时代码编译..."
    "$VENV_PYTHON" -m pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
else
    "$VENV_PYTHON" -m pip install torch torchaudio
fi
print_success "PyTorch 家族安装完成。"

# ==========================================
# 2. 解决 OpenCV 与 Numpy 纠葛
# ==========================================
print_section "安装 Numpy 与 OpenCV..."

# 显式指定 numpy >= 2 避免与旧包冲突
"$VENV_PYTHON" -m pip install "numpy>=2"

if [ "$ARCH" = "aarch64" ]; then
    print_warning "在 aarch64 上为避免依赖不兼容的 Qt 库，安装 opencv-python-headless..."
    "$VENV_PYTHON" -m pip install opencv-python-headless
else
    "$VENV_PYTHON" -m pip install opencv-python
fi
print_success "OpenCV 安装完成。"


# ==========================================
# 3. 解决 Dlib 巨量内存消耗问题 (防 OOM 处理)
# ==========================================
print_section "安装 Face Recognition 与其依赖 Dlib..."

# 检查当前内存。如果可用内存+swap 小于 4GB，编译 dlib 必定被 out-of-memory killed。
TOTAL_MEM=$(free -m | awk '/^Mem:/{print $2}')
TOTAL_SWAP=$(free -m | awk '/^Swap:/{print $2}')
AVAILABLE_MEM=$((TOTAL_MEM + TOTAL_SWAP))

SWAP_ADDED=0
SWAP_FILE="/tmp/dlib_swapfile"

if [ "$AVAILABLE_MEM" -lt 4000 ] && [ "$ARCH" = "aarch64" ]; then
    print_warning "警告: 总可用内存 (${AVAILABLE_MEM}MB) 小于 4GB！"
    print_warning "编译 dlib 需要大量内存。现在尝试临时创建一个 4GB 的 Swap 文件以防 OOM..."

    # 创建 4G swap
    if sudo fallocate -l 4G "$SWAP_FILE" && sudo chmod 600 "$SWAP_FILE" && sudo mkswap "$SWAP_FILE" && sudo swapon "$SWAP_FILE"; then
        print_success "临时 Swap ($SWAP_FILE) 挂载成功。"
        SWAP_ADDED=1
    else
        print_error "无法创建临时 Swap 文件。如果接下来编译被 Killed 收场，请手动释放内存或修改系统可用 Swap 分区。"
    fi
fi

echo "正在编译并安装 face_recognition (将关联下载并编译 dlib, 这个过程可能长达30分钟, 请耐心等待)..."

# 安装由于网络可能中端，这里用默认 pip，遇到问题可以直接重试该脚本
"$VENV_PYTHON" -m pip install face_recognition

print_success "Face Recognition 安装完成。"

# 卸载临时 swap
if [ "$SWAP_ADDED" -eq 1 ]; then
    echo "正在卸载临时 Swap 文件..."
    sudo swapoff "$SWAP_FILE" || true
    sudo rm -f "$SWAP_FILE" || true
    print_success "临时 Swap 清理完毕。"
fi

print_success "阶段 2 完成。"
