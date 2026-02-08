# llm/local/server.py
# 本地 LLM 相关 服务
#

import time
import gson
import subprocess

from src.config import general


_server_process_chat: subprocess.Popen | None = None
_server_process_embed: subprocess.Popen | None = None


def _convert_model_name_to_filepath(model_name: str) -> str:
    """
    将模型名称转换为文件名
    """

    # load model mapping
    with open(general.OFFLINE_MODEL_DIR / "mapping.json", "r") as f:
        model_mappings: dict[str, str] = gson.loads(f.read())
    
    filename = model_mappings.get(model_name, "")

    if not filename: return "" # 未找到对应文件名
    return (general.OFFLINE_MODEL_DIR / filename).as_posix()
    

def start_local_chat_server() -> bool:
    """
    启动本地 LLM 服务
    """

    global _server_process_chat
    if _server_process_chat is not None:
        return True  # 已经启动

    model_filepath = _convert_model_name_to_filepath(general.DEFAULT_OFFLINE_CHAT_MODEL)
    if not model_filepath:
        return False  # 模型文件不存在

    command = [
        (general.BACKEND_ROOT_DIR / "venv" / "bin" / "python").as_posix(),
        "-m", "llama_cpp.server",
        "--model", model_filepath,
        "--n_gpu_layers", "0",
        "--n_ctx", str(general.OFFLINE_MODEL_CTX_LEN),
        "--n_threads", str(general.OFFLINE_MODEL_THREADS - 1), # 留一个线程给 Embedding 服务
        "--verbose", "False",
        "--host", "0.0.0.0",
        "--port", "8080"
    ]

    _server_process_chat = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    time.sleep(5)  # 等待服务启动

    if _server_process_chat.poll() is not None:
        _server_process_chat = None
        return False  # 启动失败

    return True


def start_local_embed_server() -> bool:
    """
    启动本地 Embedding 服务
    """

    global _server_process_embed
    if _server_process_embed is not None:
        return True  # 已经启动

    model_filepath = _convert_model_name_to_filepath(general.DEFAULT_OFFLINE_EMBED_MODEL)
    if not model_filepath:
        return False  # 模型文件不存在

    command = [
        (general.BACKEND_ROOT_DIR / "venv" / "bin" / "python").as_posix(),
        "-m", "llama_cpp.server",
        "--model", model_filepath,
        "--n_gpu_layers", "0",
        "--n_ctx", str(general.OFFLINE_MODEL_CTX_LEN),
        "--n_threads", "1", # Embedding 服务只用一个线程
        "--verbose", "False",
        "--host", "0.0.0.0",
        "--port", "8081"
    ]

    _server_process_embed = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    time.sleep(5)  # 等待服务启动

    if _server_process_embed.poll() is not None:
        _server_process_embed = None
        return False  # 启动失败

    return True


def stop_local_chat_server() -> bool:
    """
    停止本地 LLM 服务
    """

    global _server_process_chat
    if _server_process_chat is None:
        return True  # 未启动

    _server_process_chat.terminate()
    _server_process_chat = None

    return True


def stop_local_embed_server() -> bool:
    """
    停止本地 Embedding 服务
    """

    global _server_process_embed    
    if _server_process_embed is None:
        return True  # 未启动

    _server_process_embed.terminate()
    _server_process_embed = None

    return True


def start_local_llm_server() -> bool:
    """
    启动本地 LLM 服务和 Embedding 服务
    """

    print("Starting chat server...")
    chat_started = start_local_chat_server()
    if not chat_started:
        print("Failed to start chat server!!")
        return False

    print("Starting embed server...")
    embed_started = start_local_embed_server()
    if not embed_started:
        print("Failed to start embed server!!")
        return False

    return True


def stop_local_llm_server() -> bool:
    """
    停止本地 LLM 服务和 Embedding 服务
    """

    print("Stopping chat server...")
    chat_stopped = stop_local_chat_server()
    print("Stopping embed server...")
    embed_stopped = stop_local_embed_server()

    return chat_stopped and embed_stopped


__all__ = [
    "start_local_llm_server",
    "stop_local_llm_server",
]