#!/bin/bash
# install_all.sh - UFC-2026 后端依赖总分发器

# 启用严格模式
set -euo pipefail

# 获取当前脚本所在目录
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 导入公共变量与工具函数
source "$DIR/00_env.sh"

# 优雅的清理/异常收集机制
cleanup() {
    local rc=$?
    if [ $rc -ne 0 ]; then
        echo -e "\n${BOLD}${RED}================================================${NC}"
        echo -e "${BOLD}${RED}[致命错误] 总装程序异常终止！${NC}"
        echo -e "${YELLOW}可能存在的处理方案：
 1. 检查日志上方红色报错，了解是由哪个子脚本引发的故障。
 2. 比如是在 02_core_ai_frameworks.sh 时发生 Killed（提示内存不足/OOM），考虑增加设备的 swap，然后可以直接运行 ./02_core_ai_frameworks.sh 继续，无需从 01 开始。
 3. 如果是由网络导致 pip 下载失败，直接再次运行 $0 即可，pip 有断点下载功能。${NC}"
        echo -e "${BOLD}${RED}================================================${NC}\n"
    fi
    exit $rc
}
trap cleanup EXIT

echo -e "${BOLD}${GREEN}"
echo "================================================"
echo "    UFC-2026 后端依赖智能安装向导 (ARM64 特护版)"
echo "================================================"
echo -e "${NC}"
echo "此脚本按层级将原大杂烩脚本细分为五个隔离阶段。"
echo "若在某个步骤崩溃，建议您直接修复对应问题，然后单独执行该阶段的脚本即可。"
echo ""

# 按顺序执行五个分离的脚本
bash "$DIR/01_system_deps.sh"
bash "$DIR/02_core_ai_frameworks.sh"
bash "$DIR/03_llama_engine.sh"
bash "$DIR/04_general_deps.sh"
bash "$DIR/05_tts_and_assets.sh"

echo -e "\n${BOLD}${GREEN}================================================${NC}"
echo -e "${BOLD}${GREEN}恭喜！全部部署已成功完成！${NC}"
echo -e "${BOLD}${GREEN}================================================${NC}\n"
echo "下一步，您可以激活虚拟环境并启动后台主应用："
echo -e "  $ source venv/bin/activate"
echo -e "  $ uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload\n"
