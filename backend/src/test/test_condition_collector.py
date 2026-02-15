"""
test_condition_collector.py
condition_collector 模块测试 - 仅输出LLM结果

版本: Simple Output
- 输出用户输入
- 输出LLM生成的结果
- 无验证、无评估
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import asyncio
from src.smart_triager.triager.condition_collector import (
    collect_conditions_offline,
    collect_conditions_online,
)


TEST_CASES = [
    {
        "name": "Case 1: 胸痛症状清晰",
        "user_input": "呃，我的胸口这两天有点疼，嗯，感觉就像是胸部中央在酸痛，强度还挺强的，算是中等偏上吧。咳嗽也会疼，哎。",
    },
    {
        "name": "Case 2: 脚踝不适",
        "user_input": "哦，我的脚踝有点不舒服，嗯就是有点疼。哎哟，当初好像是扭伤过的。",
    },
    {
        "name": "Case 3: 头痛症状明确",
        "user_input": "呃，我的头很疼，嗯，从早上开始就一直疼到现在，已经有大概六七个小时了吧。疼痛程度... 我觉得算是比较严重的，特别是当我低头的时候。",
    },
    {
        "name": "Case 4: 腹部疼痛",
        "user_input": "嗯，我的腹部有点疼，从中午开始的，差不多三个小时了。感觉嗯... 就是有点不舒服吧。",
    },
    {
        "name": "Case 5: 复杂症状",
        "user_input": "啊，我右边肩膀已经疼了两三周了，嗯就是感觉很累，压得特别痛。哎呀，这好像是因为我最近工作太忙了，经常要对着电脑。疼痛程度... 我觉得还算可以，但是啊，有时候特别严重就疼得比较厉害。",
    },
]


async def test_offline(case_num: int, user_input: str):
    """Run offline test and display result"""
    result = await collect_conditions_offline(user_input)
    
    if result is None:
        print("❌ LLM returned None\n")
        return
    
    print(f"Input: {user_input}\n")
    print("Output:")
    
    if result.current_summary:
        for key, val in result.current_summary.__dict__.items():
            if val is not None:
                print(f"  {key}: {val}")
    
    if result.missing_fields:
        print("  missing_fields:")
        for field in result.missing_fields:
            print(f"    - {field.name}: {field.reason}")
    else:
        print("  missing_fields: []")
    print()


async def test_online(case_num: int, user_input: str):
    """Run online test and display result"""
    result = await collect_conditions_online(user_input)
    
    if result is None:
        print("❌ LLM returned None\n")
        return
    
    print(f"Input: {user_input}\n")
    print("Output:")
    
    if result.current_summary:
        for key, val in result.current_summary.__dict__.items():
            if val is not None:
                print(f"  {key}: {val}")
    
    if result.missing_fields:
        print("  missing_fields:")
        for field in result.missing_fields:
            print(f"    - {field.name}: {field.reason}")
    else:
        print("  missing_fields: []")
    print()


async def run_offline():
    """Run all offline tests"""
    print("\n=== Offline LLM ===\n")
    for i, case in enumerate(TEST_CASES, 1):
        print(f"[Case {i}] {case['name']}")
        await test_offline(i, case['user_input'])


async def run_online():
    """Run online tests (first 2 cases)"""
    print("\n=== Online LLM ===\n")
    for i, case in enumerate(TEST_CASES[:2], 1):
        print(f"[Case {i}] {case['name']}")
        await test_online(i, case['user_input'])


async def main():
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--online":
        await run_online()
    else:
        await run_offline()


if __name__ == "__main__":
    asyncio.run(main())
