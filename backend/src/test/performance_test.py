#!/usr/bin/env python3
"""
智能分诊工作流性能测试脚本

压力测试本地机器性能，观察离线大模型（LFM2.5）的推理速度。
循环执行一个包含5个步骤的工作流，监控运行速度、CPU和内存使用率，
并将三种指标分别保存到CSV文件中。

用法：
    python performance_test.py [--iterations N] [--output-dir DIR]

示例：
    python performance_test.py --iterations 10 --output-dir ../log
"""

import sys
import os
import asyncio
import time
import csv
import argparse
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

try:
    import psutil
except ImportError:
    print("错误：未找到psutil库。请安装：pip install psutil>=5.9.0")
    sys.exit(1)

# 将 backend 根目录加入导入路径
script_dir = os.path.dirname(__file__)
backend_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
sys.path.insert(0, backend_root)

try:
    from src import logger
except ImportError:
    logger = None  # 日志模块可选

try:
    from src.llm.offline.chat import get_offline_chat_model
    # load
    get_offline_chat_model()
except Exception as e:
    print(f"离线聊天模型加载失败: {e}")
    print("请确保模型文件存在，并且路径正确。")

try:
    from src.smart_triager.triager.workflow import (
        collect_conditions, select_clinic, collect_requirement, patch_route
    )
    from src.smart_triager.car.parser import parse_route_to_commands
    from src.smart_triager.typedef import LocationLink, ConditionCollectorOutput, Requirement
    from src.map.tools import map
except ImportError as e:
    print(f"导入失败: {e}")
    print("请确保在backend目录中运行，并且所有依赖已安装。")
    print("需要安装psutil: pip install psutil>=5.9.0")
    sys.exit(1)

# 检查地图是否成功加载
if map is None:
    print("错误：地图加载失败！请检查地图文件是否存在。")
    sys.exit(1)


# ============================================================================
# 硬编码测试数据
# ============================================================================

TEST_DATA = {
    # 步骤1: collect_conditions
    "collect_conditions": {
        "user_input": "我现在头有点疼，昨天好像是装到头了",
        "online_model": False
    },

    # 步骤2: select_clinic
    "select_clinic": {
        "conditions": {
            "body_parts": "头",
            "duration": "一天",
            "severity": "有点疼",
            "description": "头疼",
            "other_relevant_information": ["昨天好像是装到头了"]
        },
        "online_model": False
    },

    # 步骤3: collect_requirement
    "collect_requirement": {
        "user_input": "我想去拿药前上个洗手间",
        "online_model": False
    },

    # 步骤4: patch_route
    "patch_route": {
        "destination_clinic_id": "internal_clinic",
        "requirement_summary": [
            {"when": "拿药前", "what": "上洗手间"}
        ],
        "origin_route": [
            {"this": "entrance", "next": "registration_center"},
            {"this": "registration_center", "next": "internal_clinic"},
            {"this": "internal_clinic", "next": "payment_center"},
            {"this": "payment_center", "next": "pharmacy"},
            {"this": "pharmacy", "next": "quit"}
        ],
        "online_model": False
    },

    # 步骤5: parse_commands
    "parse_commands": {
        "origin_route": [
            {"this": "entrance", "next": "registration_center"},
            {"this": "registration_center", "next": "internal_clinic"},
            {"this": "internal_clinic", "next": "payment_center"},
            {"this": "payment_center", "next": "pharmacy"},
            {"this": "pharmacy", "next": "toilet"},
            {"this": "toilet", "next": "quit"}
        ]
    }
}


# ============================================================================
# 性能监控类
# ============================================================================

class PerformanceMonitor:
    """监控系统资源使用情况"""

    def __init__(self):
        self.process = psutil.Process()
        self.last_cpu_times = self.process.cpu_times()

    def get_cpu_usage(self) -> float:
        """获取当前CPU使用率（百分比）"""
        return self.process.cpu_percent(interval=0.1)

    def get_cpu_times(self) -> Tuple[float, float]:
        """获取CPU时间（用户时间，系统时间）增量"""
        current_times = self.process.cpu_times()
        user_diff = current_times.user - self.last_cpu_times.user
        system_diff = current_times.system - self.last_cpu_times.system
        self.last_cpu_times = current_times
        return user_diff, system_diff

    def get_memory_usage(self) -> Tuple[float, float]:
        """获取内存使用情况（RSS, VMS）"""
        mem_info = self.process.memory_info()
        # RSS (Resident Set Size) in MB
        rss_mb = mem_info.rss / (1024 * 1024)
        # VMS (Virtual Memory Size) in MB
        vms_mb = mem_info.vms / (1024 * 1024)
        return rss_mb, vms_mb


# ============================================================================
# 数据记录类
# ============================================================================

class PerformanceRecorder:
    """记录性能数据到CSV文件"""

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)

        # 初始化CSV文件
        self.speed_file = os.path.join(self.output_dir, f"performance_speed_{self.timestamp}.csv")
        # self.cpu_file = os.path.join(self.output_dir, f"performance_cpu_{self.timestamp}.csv")
        # self.memory_file = os.path.join(self.output_dir, f"performance_memory_{self.timestamp}.csv")

        self._init_csv_files()

    def _init_csv_files(self):
        """初始化CSV文件头"""
        # 速度文件
        with open(self.speed_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'iteration', 'step_name', 'execution_time_seconds', 'success'])

        # # CPU文件
        # with open(self.cpu_file, 'w', newline='', encoding='utf-8') as f:
        #     writer = csv.writer(f)
        #     writer.writerow(['timestamp', 'iteration', 'step_name', 'cpu_percent', 'cpu_user_time', 'cpu_system_time'])

        # # 内存文件
        # with open(self.memory_file, 'w', newline='', encoding='utf-8') as f:
        #     writer = csv.writer(f)
        #     writer.writerow(['timestamp', 'iteration', 'step_name', 'memory_rss_mb', 'memory_vms_mb'])

    def record_speed(self, iteration: int, step_name: str, execution_time: float, success: bool):
        """记录执行速度数据"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        with open(self.speed_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, iteration, step_name, execution_time, success])

    # def record_cpu(self, iteration: int, step_name: str, cpu_percent: float, cpu_user_time: float, cpu_system_time: float):
    #     """记录CPU使用数据"""
    #     timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    #     with open(self.cpu_file, 'a', newline='', encoding='utf-8') as f:
    #         writer = csv.writer(f)
    #         writer.writerow([timestamp, iteration, step_name, cpu_percent, cpu_user_time, cpu_system_time])

    # def record_memory(self, iteration: int, step_name: str, rss_mb: float, vms_mb: float):
    #     """记录内存使用数据"""
    #     timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    #     with open(self.memory_file, 'a', newline='', encoding='utf-8') as f:
    #         writer = csv.writer(f)
    #         writer.writerow([timestamp, iteration, step_name, rss_mb, vms_mb])


# ============================================================================
# 工作流测试类
# ============================================================================

class WorkflowTester:
    """执行工作流测试并收集性能数据"""

    def __init__(self, recorder: PerformanceRecorder):
        self.recorder = recorder
        self.monitor = PerformanceMonitor()

    # def _reset_llm_instances(self):
    #     """重置LLM实例，避免llama_decode错误"""
    #     # 重置离线聊天模型实例
    #     offline_chat_model = None
    #     # 重新导入以更新模块级变量
    #     import importlib
    #     import src.llm.offline.chat as chat_module
    #     importlib.reload(chat_module)
    #     # 更新当前模块的引用
    #     globals()['offline_chat_model'] = None

    def test_step(self, step_name: str, iteration: int, step_func, *args, **kwargs) -> bool:
        """测试单个步骤，记录性能数据"""
        print(f"  步骤 {step_name}")

        # 记录开始前资源状态
        cpu_before = self.monitor.get_cpu_usage()
        user_time_before, sys_time_before = self.monitor.get_cpu_times()
        mem_before = self.monitor.get_memory_usage()

        start_time = time.time()
        success = False
        result = None
        exception = None

        try:
            # 执行步骤
            if asyncio.iscoroutinefunction(step_func):
                # 使用 asyncio.run() 确保每个异步函数在独立的事件循环中运行
                result = asyncio.run(step_func(*args, **kwargs))
            else:
                result = step_func(*args, **kwargs)

            # 检查结果
            if result is not None:
                success = True

        except Exception as e:
            exception = e

        execution_time = time.time() - start_time

        # 记录结束后资源状态
        cpu_after = self.monitor.get_cpu_usage()
        user_time_after, sys_time_after = self.monitor.get_cpu_times()
        mem_after = self.monitor.get_memory_usage()

        # 计算增量
        cpu_user_time = user_time_after - user_time_before
        cpu_system_time = sys_time_after - sys_time_before

        # 打印结果
        print(f"    执行时间: {execution_time:.2f}s")
        print(f"    CPU使用: {cpu_after:.1f}%")
        print(f"    内存使用: {mem_after[0]:.1f}MB")

        if success:
            print(f"    状态: ✓ 成功")
        elif exception is not None:
            print(f"    状态: ✗ 异常: {exception}")
        else:
            print(f"    状态: ✗ 失败 (返回None)")

        # 记录到CSV
        self.recorder.record_speed(iteration, step_name, execution_time, success)
        # self.recorder.record_cpu(iteration, step_name, cpu_after, cpu_user_time, cpu_system_time)
        # self.recorder.record_memory(iteration, step_name, *mem_after)

        return success

    def run_workflow(self, iteration: int) -> bool:
        """运行完整的工作流（5个步骤）"""
        print(f"\n==========================================")
        print(f"迭代 {iteration} - 开始")
        print(f"==========================================")

        step_results = []

        # 步骤1: collect_conditions
        step_data = TEST_DATA["collect_conditions"]
        success = self.test_step(
            "collect_conditions", iteration,
            collect_conditions,
            user_input=step_data["user_input"],
            online_model=step_data["online_model"]
        )
        step_results.append(success)

        # 步骤2: select_clinic
        step_data = TEST_DATA["select_clinic"]
        # 需要将字典转换为ConditionCollectorOutput对象
        conditions = ConditionCollectorOutput(**step_data["conditions"])
        success = self.test_step(
            "select_clinic", iteration,
            select_clinic,
            conditions=conditions,
            online_model=step_data["online_model"]
        )
        step_results.append(success)

        # 步骤3: collect_requirement
        step_data = TEST_DATA["collect_requirement"]
        success = self.test_step(
            "collect_requirement", iteration,
            collect_requirement,
            user_input=step_data["user_input"],
            online_model=step_data["online_model"]
        )
        step_results.append(success)

        # 步骤4: patch_route
        step_data = TEST_DATA["patch_route"]
        # 转换origin_route为LocationLink对象列表
        origin_route = [LocationLink(**link) for link in step_data["origin_route"]]
        # 转换requirement_summary为Requirement对象列表
        requirement_summary = [Requirement(**req) for req in step_data["requirement_summary"]]

        success = self.test_step(
            "patch_route", iteration,
            patch_route,
            destination_clinic_id=step_data["destination_clinic_id"],
            requirement_summary=requirement_summary,
            origin_route=origin_route,
            online_model=step_data["online_model"]
        )
        step_results.append(success)

        # 步骤5: parse_commands (同步函数)
        step_data = TEST_DATA["parse_commands"]
        origin_route = [LocationLink(**link) for link in step_data["origin_route"]]

        success = self.test_step(
            "parse_commands", iteration,
            parse_route_to_commands,
            route=origin_route,
            map=map
        )
        step_results.append(success)

        print(f"\n迭代 {iteration} - 完成")
        print(f"成功步骤: {sum(step_results)}/5")

        return all(step_results)


# ============================================================================
# 辅助函数
# ============================================================================

def print_summary(total_iterations: int, successful_iterations: int, total_time: float, output_dir: str):
    """打印测试总结"""
    print(f"\n{'='*60}")
    print("性能测试完成")
    print(f"{'='*60}")
    print(f"总迭代次数: {total_iterations}")
    print(f"成功次数: {successful_iterations}")
    print(f"成功率: {successful_iterations/total_iterations*100:.1f}%" if total_iterations > 0 else "成功率: N/A")
    print(f"总执行时间: {total_time:.2f}s")
    print(f"平均迭代时间: {total_time/total_iterations:.2f}s" if total_iterations > 0 else "平均迭代时间: N/A")
    print(f"CSV文件保存到: {os.path.abspath(output_dir)}")
    print(f"{'='*60}")


# ============================================================================
# 主函数
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="智能分诊工作流性能测试",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --iterations 10 --output-dir ../log
        """
    )

    parser.add_argument(
        "--iterations", "-i",
        type=int,
        default=10,
        help="测试迭代次数（默认：10）"
    )

    parser.add_argument(
        "--output-dir", "-o",
        type=str,
        default="../../log",
        help="输出目录路径，相对于脚本位置（默认：../../log，即backend/log）"
    )


    args = parser.parse_args()


    # 准备输出目录（相对于脚本位置）
    output_dir = os.path.abspath(os.path.join(script_dir, args.output_dir))

    # 创建记录器
    recorder = PerformanceRecorder(output_dir)

    # 创建测试器
    tester = WorkflowTester(recorder)

    # 运行测试
    print(f"\n{'='*60}")
    print(f"性能测试开始 - 迭代次数: {args.iterations}")
    print(f"{'='*60}")

    successful_iterations = 0
    total_start_time = time.time()

    for i in range(1, args.iterations + 1):
        iteration_success = tester.run_workflow(i)
        if iteration_success:
            successful_iterations += 1

    total_time = time.time() - total_start_time

    # 打印总结
    print_summary(args.iterations, successful_iterations, total_time, output_dir)


if __name__ == "__main__":
    main()