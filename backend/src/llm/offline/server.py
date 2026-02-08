# llm/local/server.py
# 本地 LLM 相关 服务
#

import time
import json
import subprocess
import threading
from queue import Queue

from src.config import general
from src import logger


_server_process_chat: subprocess.Popen | None = None
_server_process_embed: subprocess.Popen | None = None
_output_buffer_chat: Queue = Queue()
_output_buffer_embed: Queue = Queue()


def _capture_output(process: subprocess.Popen, buffer: Queue, server_name: str) -> None:
    """
    Capture stdout and stderr from a subprocess and store in a queue.
    Runs in a background thread.
    
    Args:
        process: The subprocess.Popen object
        buffer: Queue to store output lines
        server_name: Name of the server for logging purposes
    """
    try:
        while True:
            # Read from stdout
            if process.stdout:
                line = process.stdout.readline()
                if line:
                    decoded_line = line.decode('utf-8', errors='replace').strip()
                    if decoded_line:
                        buffer.put(("stdout", decoded_line))
                        logger.debug(f"[{server_name}] {decoded_line}")
            
            # Check if process is still running
            if process.poll() is not None:
                break
    except Exception as e:
        logger.error(f"Error capturing output from {server_name}: {str(e)}")


def _convert_model_name_to_filepath(model_name: str) -> str:
    """
    将模型名称转换为文件名
    """

    # load model mapping
    with open(general.OFFLINE_MODEL_DIR / "mapping.json", "r") as f:
        model_mappings: dict[str, str] = json.loads(f.read())
    
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
        logger.error("聊天模型文件不存在")
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

    _server_process_chat = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    # Start thread to capture output
    capture_thread = threading.Thread(target=_capture_output, args=(_server_process_chat, _output_buffer_chat, "Chat Server"), daemon=True)
    capture_thread.start()

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
        logger.error("Embedding 模型文件不存在")
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

    _server_process_embed = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    # Start thread to capture output
    capture_thread = threading.Thread(target=_capture_output, args=(_server_process_embed, _output_buffer_embed, "Embed Server"), daemon=True)
    capture_thread.start()

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

    logger.info("Starting chat server...")
    chat_started = start_local_chat_server()

    logger.info("Starting embed server...")
    embed_started = start_local_embed_server()

    return chat_started and embed_started


def stop_local_llm_server() -> bool:
    """
    停止本地 LLM 服务和 Embedding 服务
    """

    logger.info("Stopping chat server...")
    chat_stopped = stop_local_chat_server()

    logger.info("Stopping embed server...")
    embed_stopped = stop_local_embed_server()

    return chat_stopped and embed_stopped


def check_local_chat_server_running() -> bool:
    """
    检查本地 LLM 服务是否在运行
    """

    global _server_process_chat
    return _server_process_chat is not None and _server_process_chat.poll() is None


def check_local_embed_server_running() -> bool:
    """
    检查本地 Embedding 服务是否在运行
    """

    global _server_process_embed
    return _server_process_embed is not None and _server_process_embed.poll() is None


def check_local_llm_server_running() -> bool:
    """
    检查本地 LLM 服务和 Embedding 服务是否在运行
    """

    return check_local_chat_server_running() and check_local_embed_server_running()


__all__ = [
    "start_local_llm_server",
    "stop_local_llm_server",
    "check_local_llm_server_running",
]