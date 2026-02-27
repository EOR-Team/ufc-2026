#!/bin/bash
# 04_general_deps.sh - 阶段4：大批量常规 Python 依赖安装

source "$(dirname "${BASH_SOURCE[0]}")/00_env.sh"
check_venv

VENV_PYTHON=$(get_python_cmd)
REQ_FILE="$BACKEND_DIR/requirements.txt"
TMP_REQ="/tmp/ufc_general_reqs.txt"

print_section "阶段 4/5: 安装常规 Python 分发包 (Web, Pydantic 等)"

if [ ! -f "$REQ_FILE" ]; then
    print_error "找不到 requirements.txt: $REQ_FILE"
    exit 1
fi

# 我们从 requirements.txt 中剔除已经在前面脚本或后续脚本中单独处理的顽固包和本地 whl
# 剔除内容包括：llama-cpp-python, opencv-python, face_recognition, melotts, numpy, torch系 等。
echo "正在过滤 requirements.txt..."
grep -vE 'llama-cpp|opencv|face_recognition|numpy|psutil|torch|\.whl|^\s*#|^\s*$' "$REQ_FILE" > "$TMP_REQ"

echo "将按单子安装以下包:"
cat "$TMP_REQ" | sed 's/^/  - /'
echo ""

"$VENV_PYTHON" -m pip install -r "$TMP_REQ"

print_success "常规依赖安装完成。"

# ==========================================
# psutil 处理：如果失败可以重试或提供报错
# ==========================================
echo "安装基础系统包..."
"$VENV_PYTHON" -m pip install "psutil>=5.9.0"

rm -f "$TMP_REQ"

print_success "阶段 4 完成。"
