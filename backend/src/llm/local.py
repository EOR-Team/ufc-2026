# local.py
# 启动本地 LLM 服务
#

import gson
import subprocess

from src import config


_server_process: subprocess.Popen | None = None


def _convert_model_name_to_filepath(model_name: str) -> str:
    """
    将模型名称转换为文件名
    """

    # load model mapping
    with open(config.OFFLINE_MODEL_DIR / "binding.json", "r") as f:
        model_mappings: dict[str, str] = gson.loads(f.read())
    
    filename = model_mappings.get(model_name, "")

    if not filename: return "" # 未找到对应文件名
    return (config.OFFLINE_MODEL_DIR / filename).as_posix()
    

def start_local_llm_server() -> bool:
    """
    启动本地 LLM 服务
    """

    global _server_process
    if _server_process is not None:
        return True  # 已经启动

    model_filepath = _convert_model_name_to_filepath(config.OFFLINE_MODEL)
    if not model_filepath:
        return False  # 模型文件不存在

    command = [
        (config.BACKEND_ROOT_DIR / "venv" / "bin" / "python").as_posix(),
        "-m", "llama_cpp.server",
        "--model", model_filepath,
        "--host", "0.0.0.0",
        "--port", "8080"
    ]

    _server_process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return True


def stop_local_llm_server() -> bool:
    """
    停止本地 LLM 服务
    """

    global _server_process
    if _server_process is None:
        return True  # 未启动

    _server_process.terminate()
    _server_process = None

    return True
