# test/information_collector/offline_evaluator.py
# Information collector agent offline evaluator using llama-cpp-python
#

from src import logger
from src.route_planner.information_collector import collector_information_offline


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

def _sanitize_json_like(text: str) -> str:
    """Remove markdown fences and XML-like tags; trim and normalize whitespace."""
    t = text.strip()
    # Remove code fences
    t = t.replace("```json", "").replace("```", "")
    # Remove <response> tags
    t = t.replace("<response>", "").replace("</response>", "")
    # Collapse excessive trailing whitespace per line
    return "\n".join(line.rstrip() for line in t.splitlines())


def _collect_information(user_input: str) -> str:
    """Call the offline information collector and return the result."""
    try:
        result = collector_information_offline(user_input)
        return result
    except Exception as e:
        logger.error(f"✗ Information collection failed: {e}")
        return ""


# =========================================================================
# Streamed agent run tests
# =========================================================================

def test_offline_agent_outputs():
    """Run offline evaluator with preset Chinese inputs and log outputs"""
    logger.info("=" * 60)
    logger.info("Testing offline agent outputs (information collector)")
    logger.info("=" * 60)

    for name, user_input in STREAMED_CASES:
        logger.info(f"[Case] {name}")
        try:
            result = _collect_information(user_input)
            if result:
                clean = _sanitize_json_like(result)
                logger.info("✓ Response received")
                logger.info(clean)
            else:
                logger.warning("⚠ No response produced; model may have guardrailed or configuration may be missing")
        except Exception as e:
            logger.error(f"✗ Offline evaluation failed: {e}")
        logger.info("")


# =========================================================================
# Main Test Runner
# =========================================================================

def run_all_tests():
    """Run offline information collector evaluator"""
    logger.info("╔" + "=" * 58 + "╗")
    logger.info("║" + " " * 12 + "INFORMATION COLLECTOR OFFLINE EVALUATOR" + " " * 5 + "║")
    logger.info("╚" + "=" * 58 + "╝")
    logger.info("")

    try:
        logger.info("Testing offline information collector with llama-cpp-python...")
        test_offline_agent_outputs()
    except Exception as e:
        logger.error(f"✗ Error during testing: {e}")

    logger.info("╔" + "=" * 58 + "╗")
    logger.info("║" + " " * 18 + "ALL TESTS COMPLETED" + " " * 21 + "║")
    logger.info("╚" + "=" * 58 + "╝")

if __name__ == "__main__":
    logger.setup_file_logging("/home/n1ghts4kura/Desktop/ufc-2026/backend/logs")
    run_all_tests()
