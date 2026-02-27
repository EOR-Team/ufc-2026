#!/bin/bash
# 03_llama_engine.sh - 阶段3：携带 OpenBLAS 加速的 llama.cpp 编译

source "$(dirname "${BASH_SOURCE[0]}")/00_env.sh"
check_venv

VENV_PYTHON=$(get_python_cmd)

print_section "阶段 3/5: 编译 LLaMA C++ 引擎 (携带 OpenBLAS 硬件加速)"

# 预清理缓存，防止读取之前编译失败或没有开启 BLAS 的错误轮子
"$VENV_PYTHON" -m pip cache remove llama_cpp_python || true

print_warning "注意: 我们正在强制要求使用 OpenBLAS 编译，请确保阶段1中的系统依赖已装齐。"
echo "如果不开启 BLAS，离线模型的推理速度会呈断崖式下跌（慢 10 倍以上）。"

CMAKE_ARGS="-DGGML_BLAS=ON -DGGML_BLAS_VENDOR=OpenBLAS" \
    "$VENV_PYTHON" -m pip install "llama-cpp-python[all]" --no-binary llama-cpp-python

print_success "LLaMA C++ 引擎编译并安装完成。"

print_success "阶段 3 完成。"
