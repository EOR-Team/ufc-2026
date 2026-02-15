"""
test_condition_collector.py
测试 condition_collector 模块的功能和输出格式

版本: Enhanced with Prettier Output & New Evaluating Standards
- 通过interjections识别患者的情感信号
- 严格要求duration为时间范围而非单个时间点
- 通过logit_bias进行token概率引导
- 对optional字段（description, other_relevant_information）进行灵活处理
- 清晰区分REQUIRED与OPTIONAL字段
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))  # backend 目录

import asyncio
import json
from pydantic import ValidationError
from src.smart_triager.triager.condition_collector import (
    collect_conditions_online,
    collect_conditions_offline,
    condition_collector_instructions,
)
from src.smart_triager.typedef import ConditionCollectorOutput
from src.llm.offline import get_offline_chat_model


# ============================================================================
# 测试用例数据 - Enhanced Test Cases
# ============================================================================

TEST_CASES = [
    {
        "name": "Case 1: 胸痛症状清晰 - 所有REQUIRED字段都有明确信息",
        "user_input": "呃，我的胸口这两天有点疼，嗯，感觉就像是胸部中央在酸痛，强度还挺强的，算是中等偏上吧。咳嗽也会疼，哎。",
        "analysis": {
            "body_parts": "胸口 / 胸部中央",
            "duration": "这两天 (时间范围)",
            "severity": "中等偏上 (清晰的主观感受)",
            "interjections": "呃、嗯、哎 - 强化患者的真实感受和困扰程度",
        },
        "expected_has_summary": True,
        "expected_has_required_fields": True,  # body_parts, duration, severity都存在
        "expected_missing_count": 0,
    },
    {
        "name": "Case 2: 脚踝不适 - 严重程度描述不够清晰准确",
        "user_input": "哦，我的脚踝有点不舒服，嗯就是有点疼。哎哟，当初好像是扭伤过的。",
        "analysis": {
            "body_parts": "脚踝 (清晰)",
            "duration": "没有明确的时间范围信息",
            "severity": "有点不舒服 / 有点疼 (不够清晰，需要更准确的描述)",
            "other_info": "扭伤历史 (相关背景信息)",
        },
        "expected_has_summary": True,
        "expected_has_required_fields": False,  # severity 或 duration 不够清晰
        "expected_missing_count": 1,  # severity 字段应在 missing_fields
    },
    {
        "name": "Case 3: 头痛症状明确 - 清晰的时间范围和严重程度",
        "user_input": "呃，我的头很疼，嗯，从早上开始就一直疼到现在，已经有大概六七个小时了吧。疼痛程度... 我觉得算是比较严重的，特别是当我低头的时候。",
        "analysis": {
            "body_parts": "头",
            "duration": "从早上到现在，六七个小时 (清晰的时间范围)",
            "severity": "比较严重的 (清晰的主观感受)",
            "interjections": "呃、嗯、... - 表达了患者的思考和确定过程",
        },
        "expected_has_summary": True,
        "expected_has_required_fields": True,
        "expected_missing_count": 0,
    },
    {
        "name": "Case 4: 腹部疼痛 - 时间范围清晰但严重程度不够准确",
        "user_input": "嗯，我的腹部有点疼，从中午开始的，差不多三个小时了。感觉嗯... 就是有点不舒服吧。",
        "analysis": {
            "body_parts": "腹部 (清晰)",
            "duration": "从中午开始，三个小时 (时间范围清晰)",
            "severity": "有点不舒服 (不够清晰和准确，需要进一步说明)",
            "interjections": "嗯 - 表达了患者的犹豫和不确定",
        },
        "expected_has_summary": True,
        "expected_has_required_fields": False,  # severity 不够清晰
        "expected_missing_count": 1,  # severity 字段应在 missing_fields
    },
    {
        "name": "Case 5: 复杂症状 - 所有REQUIRED字段清晰+背景信息补充",
        "user_input": "啊，我右边肩膀已经疼了两三周了，嗯就是感觉很累，压得特别痛。哎呀，这好像是因为我最近工作太忙了，经常要对着电脑。疼痛程度... 我觉得还算可以，但是啊，有时候特别严重就疼得比较厉害。",
        "analysis": {
            "body_parts": "右边肩膀",
            "duration": "两三周 (清晰的时间范围)",
            "severity": "压得特别痛、有时特别严重 (比较清晰的主观感受)",
            "other_info": "工作繁忙、经常对着电脑 (相关背景信息)",
            "interjections": "啊、嗯、哎呀、... - 强化患者的困扰和诉说的急切感",
        },
        "expected_has_summary": True,
        "expected_has_required_fields": True,
        "expected_missing_count": 0,
    },
]


# ============================================================================
# 验证函数 - Validation Functions
# ============================================================================

def validate_output(output: ConditionCollectorOutput) -> dict:
    """
    验证输出是否符合 ConditionCollectorOutput 的数据结构要求。
    
    评估标准 (Enhanced Version):
    ✓ current_summary 必须存在
    ✓ 3 REQUIRED 字段必须全部存在: duration, severity, body_parts
    ✓ missing_fields 应该基于字段的 CLARITY 和 ACCURACY 来判断
    ✓ description (OPTIONAL): 如果存在就包含，不存在不要求
    ✓ other_relevant_information (OPTIONAL): 背景信息，不影响强制字段判断
    ✓ missing_fields 中的每个字段都要有清晰的理由
    
    Returns:
        dict: {
            "valid": bool,                    # 整体是否有效
            "has_summary": bool,              # current_summary 是否存在
            "has_required_fields": bool,      # 3个REQUIRED字段都存在
            "missing_count": int,             # missing_fields的数量
            "details": dict                   # 详细的字段检查信息
        }
    """
    result = {
        "valid": False,
        "has_summary": False,
        "has_required_fields": False,
        "missing_count": 0,
        "details": {}
    }
    
    if output is None:
        result["details"]["error"] = "Output is None"
        return result

    # 检查 current_summary 是否存在
    if output.current_summary is None:
        result["details"]["error"] = "current_summary is missing"
        return result
    
    result["has_summary"] = True

    # 检查 missing_fields 是否为列表
    if not isinstance(output.missing_fields, list):
        result["details"]["error"] = "missing_fields is not a list"
        return result
    
    result["missing_count"] = len(output.missing_fields)

    # 检查 REQUIRED 字段是否都存在
    required_fields = {
        'body_parts': '身体部位 (Body Parts)',
        'duration': '症状持续时间 (Duration)',
        'severity': '疼痛/症状严重程度 (Severity)'
    }
    
    field_status = {}
    all_required_present = True
    
    for field_name, field_display in required_fields.items():
        has_field = hasattr(output.current_summary, field_name) and getattr(output.current_summary, field_name) is not None
        field_status[field_name] = {
            "display": field_display,
            "present": has_field,
            "value": getattr(output.current_summary, field_name, None) if has_field else None
        }
        if not has_field:
            all_required_present = False
    
    result["has_required_fields"] = all_required_present
    result["details"]["required_fields"] = field_status
    
    # 检查 OPTIONAL 字段
    optional_fields = {}
    
    if hasattr(output.current_summary, 'description') and output.current_summary.description:
        optional_fields['description'] = output.current_summary.description
    
    if hasattr(output.current_summary, 'other_relevant_information') and output.current_summary.other_relevant_information:
        optional_fields['other_relevant_information'] = output.current_summary.other_relevant_information
    
    result["details"]["optional_fields"] = optional_fields
    
    # 检查 missing_fields 是否合理
    missing_fields_info = []
    for field in output.missing_fields:
        missing_fields_info.append({
            "name": field.name,
            "reason": field.reason
        })
    
    result["details"]["missing_fields_info"] = missing_fields_info
    
    # 整体有效性：需要有summary且有REQUIRED字段
    result["valid"] = result["has_summary"] and result["has_required_fields"]
    
    return result




# ============================================================================
# 测试函数 - Test Functions
# ============================================================================

def format_result(passed: bool) -> str:
    """格式化测试结果"""
    return "✅" if passed else "❌"


async def test_case_offline(test_case: dict, case_num: int):
    """Test single case with offline LLM - concise output"""
    user_input = test_case["user_input"]
    case_name = test_case["name"]

    print(f"\n[Case {case_num}] {case_name}")
    print(f"Input: {user_input[:60]}..." if len(user_input) > 60 else f"Input: {user_input}")
    
    try:
        result = await collect_conditions_offline(user_input)
        validation = validate_output(result)
        
        if not validation["valid"]:
            print(f"  {format_result(False)} Validation failed")
            return False

        has_summary = validation["has_summary"]
        has_required = validation["has_required_fields"]
        missing_count = validation["missing_count"]
        
        expected_has_summary = test_case["expected_has_summary"]
        expected_required = test_case["expected_has_required_fields"]
        expected_missing = test_case["expected_missing_count"]
        
        all_passed = (
            has_summary == expected_has_summary and 
            has_required == expected_required and
            missing_count == expected_missing
        )
        
        if all_passed:
            body = validation['details']['required_fields']['body_parts']['value']
            dur = validation['details']['required_fields']['duration']['value']
            sev = validation['details']['required_fields']['severity']['value']
            print(f"  {format_result(True)} body_parts={body}, duration={dur}, severity={sev}")
            if missing_count > 0:
                missing_names = ', '.join([m['name'] for m in validation['details']['missing_fields_info']])
                print(f"     Missing: {missing_names}")
            return True
        else:
            print(f"  {format_result(False)} Expected(summary={expected_has_summary}, required={expected_required}, missing={expected_missing})")
            print(f"              Got(summary={has_summary}, required={has_required}, missing={missing_count})")
            return False

    except Exception as e:
        print(f"  {format_result(False)} Error: {str(e)[:80]}")
        return False


async def test_case_online(test_case: dict, case_num: int):
    """Test single case with online LLM - concise output"""
    user_input = test_case["user_input"]
    case_name = test_case["name"]

    print(f"\n[Case {case_num}] {case_name}")
    print(f"Input: {user_input[:60]}..." if len(user_input) > 60 else f"Input: {user_input}")
    
    try:
        result = await collect_conditions_online(user_input)
        validation = validate_output(result)
        
        if not validation["valid"]:
            print(f"  {format_result(False)} Validation failed")
            return False

        body = validation['details']['required_fields']['body_parts']['value']
        dur = validation['details']['required_fields']['duration']['value']
        sev = validation['details']['required_fields']['severity']['value']
        print(f"  {format_result(True)} body_parts={body}, duration={dur}, severity={sev}")
        return True

    except Exception as e:
        print(f"  {format_result(False)} Error: {str(e)[:80]}")
        return False


# ============================================================================
# 主测试函数 - Main Test Runners
# ============================================================================

async def run_tests_offline():
    """Run all offline LLM test cases"""
    print("\n🧪 Offline LLM Test Suite\n")

    passed = 0
    failed = 0

    for i, test_case in enumerate(TEST_CASES, 1):
        success = await test_case_offline(test_case, i)
        if success:
            passed += 1
        else:
            failed += 1

    total = passed + failed
    print(f"\n{'─' * 60}")
    print(f"Results: {passed}/{total} passed ({passed/total*100:.0f}%)")
    print(f"{'─' * 60}")
    
    return failed == 0


async def run_tests_online():
    """Run first 2 online LLM test cases (to save API costs)"""
    print("\n🧪 Online LLM Test Suite\n")

    passed = 0
    failed = 0

    for i, test_case in enumerate(TEST_CASES[:2], 1):
        success = await test_case_online(test_case, i)
        if success:
            passed += 1
        else:
            failed += 1

    total = passed + failed
    print(f"\n{'─' * 60}")
    print(f"Results: {passed}/{total} passed ({passed/total*100:.0f}%)")
    print(f"note: only first 2 cases run in online mode to save API costs")
    print(f"{'─' * 60}")
    
    return failed == 0


async def main():
    """Main entry point"""
    import sys

    print("\n🏥 Condition Collector Test Suite - Offline LLM")
    print("   Enhanced with interjection recognition & logit bias\n")

    if len(sys.argv) > 1 and sys.argv[1] == "--online":
        result = await run_tests_online()
    else:
        result = await run_tests_offline()

    if result:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
