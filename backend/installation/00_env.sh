#!/bin/bash
# 00_env.sh - 环境变量与公共函数库

# 启用严格模式：有任何错误立刻退出，未定义变量报错，管道中任一步错误都报错
set -euo pipefail

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# 关键路径定义
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$BACKEND_DIR/venv"

# 全局环境变量
export HF_ENDPOINT="https://hf-mirror.com"
export PIP_NO_CACHE_DIR=1  # 在资源受限的 ARM 设备上，防止 pip 缓存撑爆磁盘

# ==========================================
# 打印工具函数
# ==========================================
print_section() {
    echo -e "\n${BOLD}${BLUE}================================================${NC}"
    echo -e "${BOLD}${BLUE}>>> $1${NC}"
    echo -e "${BOLD}${BLUE}================================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}[✓] $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[!] $1${NC}"
}

print_error() {
    echo -e "\n${RED}${BOLD}[FATAL ERROR] $1${NC}"
}

# 错误处理钩子
handle_error() {
    local exit_code=$?
    local line_no=$1
    local command="$2"
    print_error "命令执行失败 (退出码: $exit_code)"
    echo -e "${RED}发生错误的代码行: $line_no${NC}"
    echo -e "${RED}执行的命令: $command${NC}"
    echo -e "${YELLOW}提示: 上述输出中包含详细的报错信息。请修复错误后，重新运行当前脚本或 install_all.sh。${NC}"
    exit $exit_code
}

# 绑定 ERR 信号到钩子函数，这样任何未捕获的错误都会被高亮显示
trap 'handle_error ${LINENO} "$BASH_COMMAND"' ERR

# ==========================================
# 环境检测函数
# ==========================================
get_python_cmd() {
    if [ -f "$VENV_DIR/bin/python" ]; then
        echo "$VENV_DIR/bin/python"
    else
        echo ""
    fi
}

check_venv() {
    local py_cmd=$(get_python_cmd)
    if [ -z "$py_cmd" ]; then
        print_error "未找到虚拟环境，请先运行 01_system_deps.sh 创建环境。"
        exit 1
    fi
}
