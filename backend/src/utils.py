# utils.py
# 一些工具

import os
import json
from src.config.general import OFFLINE_MODEL_TYPES, OFFLINE_MODEL_DIR


def convert_model_name_to_path(model: OFFLINE_MODEL_TYPES) -> str:
    """
    将模型名称转换为模型文件路径

    Args:
        model_name (OFFLINE_MODEL_TYPES): 模型名称

    Returns:
        str: 模型文件路径
    """

    with open(OFFLINE_MODEL_DIR / "mapping.json", "r", encoding="utf-8") as f:
        model_mapping: dict[str, str] = json.loads(f.read())
    
    if model not in model_mapping:
        return ""
    
    model_filename = model_mapping[model]
    model_path = OFFLINE_MODEL_DIR / model_filename

    return model_path.resolve().as_posix()


def remove_os_environ_proxies() -> None:
    """
    移除所有与代理相关的环境变量，防止 httpx 使用 SOCKS 代理时出现问题
    必须在导入 agents 之前调用
    """
    proxy_vars = [
        'http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY',
        'all_proxy', 'ALL_PROXY',
        'SOCKS_PROXY', 'socks_proxy',
        'ftp_proxy', 'FTP_PROXY',
        'no_proxy', 'NO_PROXY'
    ]

    for var in proxy_vars:
        os.environ.pop(var, None)

    # 设置显式空值以确保没有代理
    os.environ['NO_PROXY'] = '*'


def load_file_to_str(file_path: str) -> str:
    """
    将文件内容加载为字符串

    Args:
        file_path (str): 文件路径

    Returns:
        str: 文件内容字符串
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    return content
