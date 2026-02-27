#!/bin/bash
# 01_system_deps.sh - 阶段1：系统环境与虚拟环境初始化

source "$(dirname "${BASH_SOURCE[0]}")/00_env.sh"

print_section "阶段 1/5: 系统环境与虚拟环境初始化"

# ==========================================
# 1. 检查和安装 ARM64 系统核心依赖
# ==========================================
ARCH=$(uname -m)
if [ "$ARCH" = "aarch64" ]; then
    print_warning "检测到 ARM64 平台 (aarch64)。准备安装系统依赖（需要 sudo 权限）。"

    # 检测 apt 包管理器是否存在
    if command -v apt-get >/dev/null 2>&1; then
        echo "更新 apt 包索引..."
        sudo apt-get update

        echo "安装构建工具链、CMake 及 OpenBLAS 加速库..."
        sudo apt-get install -y build-essential cmake pkg-config \
                                libopenblas-dev liblapack-dev libatlas-base-dev

        # dlib 编译需要的 boost
        sudo apt-get install -y libboost-all-dev

        print_success "ARM64 系统依赖安装完成。"
    else
        print_warning "未检测到 apt 包管理器，请确保系统中已安装构建工具链及 OpenBLAS。"
    fi
else
    print_success "当前架构 ($ARCH) 非 ARM64，系统依赖步骤跳过安全检查，默认依赖已满足。"
fi

# ==========================================
# 2. 检查 Python 版本并创建虚拟环境
# ==========================================
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
    print_error "未找到 Python 3.10，本项目严格要求 Python 3.10.x（建议 3.10.13）\n请安装后重试 (推荐通过 pyenv)。"
    exit 1
fi

print_success "找到基础 Python 解释器: $PYTHON_CMD ($($PYTHON_CMD --version))"

if [ ! -d "$VENV_DIR" ]; then
    print_warning "正在创建虚拟环境于: $VENV_DIR"
    "$PYTHON_CMD" -m venv "$VENV_DIR"
    print_success "虚拟环境创建成功。"
else
    print_success "虚拟环境已存在: $VENV_DIR"
fi

# ==========================================
# 3. 升级 pip
# ==========================================
VENV_PYTHON=$(get_python_cmd)
echo "正在升级 pip..."
"$VENV_PYTHON" -m pip install --upgrade pip

print_success "阶段 1 完成。"
