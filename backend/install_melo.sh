#!/bin/bash
# install_melo.sh - 自动安装 MeloTTS 和字典

set -e

echo "========================================"
echo "  MeloTTS 自动安装脚本"
echo "========================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 成功/失败计数
SUCCESS=0
FAILED=0

# 检查命令是否存在
check_cmd() {
    if command -v "$1" &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# 打印状态
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}[✓]${NC} $2"
        ((SUCCESS++))
    else
        echo -e "${RED}[✗]${NC} $2"
        ((FAILED++))
    fi
}

# ========================================
# 1. 检查环境
# ========================================
echo ""
echo ">>> 检查环境..."

# 检查 Python
if check_cmd python; then
    PYTHON_CMD="python"
elif check_cmd python3; then
    PYTHON_CMD="python3"
else
    echo -e "${RED}[✗] 未找到 Python，请先安装 Python 3.10+${NC}"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}[✓]${NC} Python 版本: $PYTHON_VERSION"

# 检查 pip
if ! check_cmd pip; then
    $PYTHON_CMD -m ensurepip --upgrade
fi
echo -e "${GREEN}[✓]${NC} pip 已就绪"

# ========================================
# 2. 查找 whl 包
# ========================================
echo ""
echo ">>> 查找 MeloTTS 安装包..."

WHL_FILE=$(find . -maxdepth 1 -name "melotts*.whl" -o -name "melo*.whl" 2>/dev/null | head -n 1)

if [ -z "$WHL_FILE" ]; then
    echo -e "${RED}[✗] 未找到 melotts*.whl 或 melo*.whl 文件${NC}"
    echo "请确保 whl 文件在当前目录下"
    exit 1
fi

echo -e "${GREEN}[✓]${NC} 找到安装包: $WHL_FILE"

# ========================================
# 3. 安装 MeloTTS
# ========================================
echo ""
echo ">>> 安装 MeloTTS..."

 $PYTHON_CMD -m pip install --upgrade pip --quiet
 $PYTHON_CMD -m pip install "$WHL_FILE" --quiet

if [ $? -eq 0 ]; then
    print_status 0 "MeloTTS 安装成功"
else
    print_status 1 "MeloTTS 安装失败"
    exit 1
fi

# ========================================
# 4. 查找并安装字典
# ========================================
echo ""
echo ">>> 查找并安装字典..."

# 检查本地字典文件
DICT_FILE=$(find . -maxdepth 1 -name "unidic*.zip" 2>/dev/null | head -n 1)

if [ -n "$DICT_FILE" ]; then
    echo -e "${GREEN}[✓]${NC} 找到本地字典: $DICT_FILE"
    echo ">>> 从本地安装字典..."
    
    # 获取 unidic 安装路径
    UNIDIC_PATH=$($PYTHON_CMD -c "import unidic; print(unidic.DICDIR)" 2>/dev/null || echo "")
    
    if [ -n "$UNIDIC_PATH" ]; then
        # 解压字典
        mkdir -p "$UNIDIC_PATH"
        unzip -o -q "$DICT_FILE" -d "$UNIDIC_PATH"
        print_status $? "字典解压完成"
    else
        # 回退到下载
        echo -e "${YELLOW}[!]${NC} 无法获取字典路径，尝试在线下载..."
        $PYTHON_CMD -m unidic download
        print_status $? "字典下载完成"
    fi
else
    echo -e "${YELLOW}[!]${NC} 未找到本地字典，尝试在线下载..."
    $PYTHON_CMD -m unidic download
    print_status $? "字典下载完成"
fi

# ========================================
# 5. 检测安装结果
# ========================================
echo ""
echo ">>> 检测安装结果..."

# 检测导入
echo "测试导入模块..."
IMPORT_TEST=$($PYTHON_CMD -c "from melo.api import TTS" 2>&1)
if [ $? -eq 0 ]; then
    print_status 0 "模块导入成功"
else
    print_status 1 "模块导入失败: $IMPORT_TEST"
fi

# 检测模型初始化
echo "测试模型初始化..."
INIT_TEST=$($PYTHON_CMD -c "
import os
import warnings
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
warnings.filterwarnings('ignore')
from melo.api import TTS
tts = TTS(language='ZH', device='cpu')
print('OK')
" 2>&1)

if [[ "$INIT_TEST" == *"OK"* ]]; then
    print_status 0 "模型初始化成功"
else
    print_status 1 "模型初始化失败"
    echo "$INIT_TEST"
fi

# 检测 TTS 合成
echo "测试语音合成..."
TTS_TEST=$($PYTHON_CMD -c "
import os
import warnings
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
warnings.filterwarnings('ignore')
from melo.api import TTS
tts = TTS(language='ZH', device='cpu')
tts.tts_to_file('测试', speaker_id=0, output_path='/tmp/melo_test.wav')
print('OK')
" 2>&1)

if [[ "$TTS_TEST" == *"OK"* ]]; then
    print_status 0 "语音合成成功"
    # 检查文件
    if [ -f "/tmp/melo_test.wav" ]; then
        FILE_SIZE=$(stat -c%s "/tmp/melo_test.wav" 2>/dev/null || stat -f%z "/tmp/melo_test.wav" 2>/dev/null)
        print_status 0 "生成音频文件: ${FILE_SIZE} bytes"
        rm -f /tmp/melo_test.wav
    fi
else
    print_status 1 "语音合成失败"
    echo "$TTS_TEST"
fi

# ========================================
# 6. 输出结果
# ========================================
echo ""
echo "========================================"
echo "  安装结果统计"
echo "========================================"
echo -e "成功: ${GREEN}$SUCCESS${NC}"
echo -e "失败: ${RED}$FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN}>>> MeloTTS 安装完成！${NC}"
    echo ""
    echo "使用示例:"
    echo "  python -c \"from melo.api import TTS; TTS(language='ZH').tts_to_file('你好', speaker_id=0, output_path='out.wav')\""
    exit 0
else
    echo ""
    echo -e "${RED}>>> 安装过程中存在错误，请检查上述输出${NC}"
    exit 1
fi