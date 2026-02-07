import json
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

try:
	import requests
except Exception:
	requests = None

from src.config import general


class OfflineAgent:
	"""一个简单的离线智能体，可以与本地 OpenAI 兼容的 LLM 服务器通信
	（例如 llama.cpp 的 OpenAI 兼容端点）并可以调用已注册的工具。

	模型响应使用的工具调用协议（用于演示/测试）：
	  TOOL_CALL|<工具名称>|<json 负载>
	示例助手回复请求工具调用：
	  TOOL_CALL|calculator|{"expr":"2+2"}
	"""

	def __init__(
		self,
		model_name: str = "",
		prompt_path: Optional[Path] = None,
		tools: Optional[Dict[str, Callable[..., Any]]] = None,
		timeout: int = 30,
	) -> None:
		self.model_name = model_name or ""
		self.timeout = timeout
		self.tools: Dict[str, Callable[..., Any]] = tools or {}

		self.prompt_path = (
			Path(prompt_path) if prompt_path else Path(__file__).parent / "prompt.md"
		)
		self.system_prompt = self._load_system_prompt()

		# 对话消息以 OpenAI 聊天消息格式存储
		self.messages: List[Dict[str, str]] = [
			{"role": "system", "content": self.system_prompt}
		]

	def _load_system_prompt(self) -> str:
		try:
			text = self.prompt_path.read_text(encoding="utf-8").strip()
			if not text:
				return "You are a helpful assistant."
			return text
		except FileNotFoundError:
			return "You are a helpful assistant."

	def register_tool(self, name: str, fn: Callable[..., Any]) -> None:
		self.tools[name] = fn

	def _http_post(self, url: str, payload: dict) -> dict:
		if requests is not None:
			resp = requests.post(url, json=payload, timeout=self.timeout)
			resp.raise_for_status()
			return resp.json()

		# 回退到标准库
		import urllib.request

		data = json.dumps(payload).encode("utf-8")
		req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
		with urllib.request.urlopen(req, timeout=self.timeout) as r:
			return json.loads(r.read().decode("utf-8"))

	def chat(self, user_message: str, max_tokens: int = 512, temperature: float = 0.2) -> dict:
		"""向离线模型发送用户消息并返回助手回复。

		如果助手使用测试协议请求工具调用，智能体将
		执行已注册的工具并返回工具结果和助手文本。
		"""
		self.messages.append({"role": "user", "content": user_message})

		url = general.OFFLINE_MODEL_HOST.rstrip("/") + "/chat/completions"

		payload = {
			"model": self.model_name,
			"messages": self.messages,
			"max_tokens": max_tokens,
			"temperature": temperature,
		}

		try:
			resp = self._http_post(url, payload)
		except Exception as e:
			return {"error": str(e)}

		# 期望的 OpenAI 兼容响应: choices[0].message
		assistant_message = None
		try:
			choice = resp.get("choices", [])[0]
			assistant_message = choice.get("message", {})
		except Exception:
			assistant_message = None

		if not assistant_message:
			return {"error": "no assistant message", "raw": resp}

		content = assistant_message.get("content", "").strip()
		role = assistant_message.get("role", "assistant")

		result: Dict[str, Any] = {"assistant": content, "raw_response": resp}

		# 将助手消息添加到历史记录
		self.messages.append({"role": role, "content": content})

		# 检测工具调用模式: TOOL_CALL|工具名称|<json>
		if content.startswith("TOOL_CALL|"):
			try:
				_, tool_name, tool_payload_raw = content.split("|", 2)
				tool_payload = json.loads(tool_payload_raw)
			except Exception as e:
				result["tool_error"] = f"invalid tool call format: {e}"
				return result

			tool = self.tools.get(tool_name)
			if tool is None:
				result["tool_error"] = f"tool '{tool_name}' not registered"
				return result

			try:
				tool_output = tool(**tool_payload) if isinstance(tool_payload, dict) else tool(tool_payload)
			except Exception as e:
				result["tool_error"] = str(e)
				return result

			# 将工具输出记录为特殊的助手/工具消息
			tool_output_text = json.dumps(tool_output, ensure_ascii=False) if not isinstance(tool_output, str) else tool_output
			self.messages.append({"role": "tool", "content": tool_output_text})
			result["tool_called"] = tool_name
			result["tool_input"] = tool_payload
			result["tool_output"] = tool_output

			# 可选：执行后续模型调用，包含工具输出以便助手继续
			follow_payload = {
				"model": self.model_name,
				"messages": self.messages,
				"max_tokens": max_tokens,
				"temperature": temperature,
			}
			try:
				follow_resp = self._http_post(url, follow_payload)
				follow_choice = follow_resp.get("choices", [])[0]
				follow_msg = follow_choice.get("message", {})
				follow_content = follow_msg.get("content", "").strip()
				self.messages.append({"role": follow_msg.get("role", "assistant"), "content": follow_content})
				result["assistant_after_tool"] = follow_content
				result["follow_raw"] = follow_resp
			except Exception as e:
				result["follow_error"] = str(e)

		return result


def _demo_calculator(expr: str = "") -> Dict[str, Any]:
	try:
		# 非常简单的安全求值演示（仅限数字和运算符）
		allowed = set("0123456789+-*/(). ")
		if not set(expr) <= allowed:
			return {"error": "unsafe expression"}
		value = eval(expr, {"__builtins__": {}})
		return {"expr": expr, "value": value}
	except Exception as e:
		return {"error": str(e)}


if __name__ == "__main__":
	# 作为脚本运行时的快速手动演示
	agent = OfflineAgent()
	agent.register_tool("calculator", lambda expr=None, **kw: _demo_calculator(expr or kw.get("expr", "")))
	print("Demo agent ready. Call agent.chat('...') to interact.")

