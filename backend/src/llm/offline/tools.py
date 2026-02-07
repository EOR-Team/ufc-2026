from typing import Any, Dict

from .agent import _demo_calculator


def echo(text: str = "") -> Dict[str, Any]:
    return {"echo": text}


def calculator(expr: str = "") -> Dict[str, Any]:
    return _demo_calculator(expr)


def load_default_tools(agent) -> None:
    """Register default test tools into an OfflineAgent instance."""
    agent.register_tool("calculator", lambda expr=None, **kw: calculator(expr or kw.get("expr", "")))
    agent.register_tool("echo", lambda text=None, **kw: echo(text or kw.get("text", "")))
