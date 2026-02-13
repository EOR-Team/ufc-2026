# utils.py
# 一些工具

import os
import subprocess


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


def check_network_connection() -> bool:
    """
    简单检查是否有网络连接
    """

    try:
        # 使用 ping 命令检查连接
        process = subprocess.Popen(['ping', '-c', '1', '8.8.8.8'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return process.wait() == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        return False