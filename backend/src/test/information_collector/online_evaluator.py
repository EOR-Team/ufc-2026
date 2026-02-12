# test/information_collector/online_evaluator.py
# Information collector agent streamed online evaluator
#

import asyncio
from openai.types.responses import ResponseTextDeltaEvent

from src import logger
from src.route_planner import information_collector as ic


# =========================================================================
# Streamed agent runs
# =========================================================================

STREAMED_CASES = [
    ("仅表达不适，缺信息", "我有点难受。"),
    ("位置含糊+症状简单", "我在那个电梯旁边，有点头晕。"),
    ("信息较完整", "我在医院大厅，头痛两天了，程度中等，主要在头部。"),
    ("位置明确+严重程度高", "我在门口，肚子很痛，很严重。"),
    ("含自定义需求", "我在急诊门口，胸口左边刺痛三天了，程度偏重，想先去趟厕所再看医生。"),
    ("缺严重程度+行为描述", "我在门诊大厅，膝盖疼了一周，走路的时候更明显。"),
    ("多症状较完整", "我在住院部一楼，头晕和恶心持续了半天，程度中等，主要是头部和胃不舒服。"),
]


async def _consume_stream(user_input: str) -> str:
    """Run collect_information and consume streamed delta events, returning concatenated text."""
    result = await ic.collect_information(user_input, use_online_model=True)
    output_chunks: list[str] = []
    try:
        async for event in result.stream_events():
            if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                delta = getattr(event.data, "delta", "")
                if isinstance(delta, str) and delta:
                    output_chunks.append(delta)
    except Exception as e:
        logger.error(f"✗ Streaming consumption failed: {e}")
    return "".join(output_chunks)


# =========================================================================
# Streamed agent run tests
# =========================================================================

def test_streamed_agent_outputs():
    """Run streamed mode with preset Chinese inputs and log outputs"""
    logger.info("=" * 60)
    logger.info("Testing streamed agent outputs")
    logger.info("=" * 60)

    for name, user_input in STREAMED_CASES:
        logger.info(f"[Case] {name}")
        try:
            streamed_text = asyncio.run(_consume_stream(user_input))
            if streamed_text:
                logger.info("✓ Streamed text received")
                logger.info(streamed_text)
            else:
                logger.warning("⚠ Stream produced no text; agent may have guardrailed or configuration may be missing")
        except Exception as e:
            logger.error(f"✗ Streamed run failed: {e}")
        logger.info("")


# =========================================================================
# Main Test Runner
# =========================================================================

def run_all_tests():
    """Run streamed evaluator"""
    logger.info("╔" + "=" * 58 + "╗")
    logger.info("║" + " " * 12 + "INFORMATION COLLECTOR ONLINE EVALUATOR" + " " * 6 + "║")
    logger.info("╚" + "=" * 58 + "╝")
    logger.info("")

    test_streamed_agent_outputs()

    logger.info("╔" + "=" * 58 + "╗")
    logger.info("║" + " " * 18 + "ALL TESTS COMPLETED" + " " * 21 + "║")
    logger.info("╚" + "=" * 58 + "╝")


if __name__ == "__main__":
    logger.setup_file_logging("/home/n1ghts4kura/Desktop/ufc-2026/backend/logs")
    run_all_tests()
