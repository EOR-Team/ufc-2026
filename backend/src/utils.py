# utils.py
# 一些工具

import os
import subprocess
from typing import Callable
from llama_cpp import Llama


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


def build_logit_bias(
    get_model_func: Callable[[], Llama],
    # ----- 分割线 -----
    string_to_probability: dict[str, float] | None = None,
    token_eos: float | None = None,
    json_block: float | None = None,
) -> Callable[[], dict[int, float]]:
    """
    根据指定模型 与 指定键值对 构建 logit bias 字典
    用于调整 键 对应token 的输出概率
    
    Args:
        get_model_func: 一个函数，返回一个 Llama 模型实例
        string_to_probability: 键为你要调整输出概率的字符串，值为你要设置的概率调整值（正数提高概率，负数降低概率）
        token_eos: 可选参数，如果提供，将对模型的结束符 token 应用这个概率调整值，进一步控制输出的完整性
    Returns:
        Callable[dict[int, float]]: 一个返回 logit_bias 字典的函数，该字典可以直接作为模型调用时的 logit_bias 参数传入
    """

    def wrapper() -> dict[int, float]:
        model = get_model_func()

        logit_bias_dict = {}
        if string_to_probability is not None:
            for string, prob in string_to_probability.items():
                token_list = model.tokenize(string.encode())
                for token in token_list: # 如果一个字符串对应多个 token，则对每个 token 都进行概率调整
                    logit_bias_dict[token] = prob

        # 可选地调整结束符 token 的概率，鼓励模型输出更完整的内容，减少输出被截断的情况发生
        if token_eos is not None:
            logit_bias_dict[model.token_eos()] = token_eos

        # 可选地调整 markdown json code block 相关 token 的概率，鼓励模型输出更纯净的 JSON 内容，减少输出被 markdown code block 包裹导致无法解析的情况发生
        if json_block is not None:
            markdown_json_block_begin_token_list = model.tokenize(b"```json") # 开始标记通常是 ```json
            markdown_json_block_end_token_list = model.tokenize(b"```") # 结束标记通常是 ``` (这里也会匹配到其他 markdown code 需要注意到)
            for token in markdown_json_block_begin_token_list + markdown_json_block_end_token_list:
                logit_bias_dict[token] = json_block

        return logit_bias_dict
    
    return wrapper


def instruction_token_wrapper(origin: str) -> str:
    """
    将 **instruction** 用 **LFM2.5** 的格式包装起来
    """

    # return f"<|startoftext|><|im_start|>system\n{origin}\n<|im_end|>"
    return origin


def input_token_wrapper(origin: str) -> str:
    """
    将 **input** 用 **LFM2.5** 的格式包装起来
    """

    # return f"<|im_start|>user{origin}<|im_end|>"
    return origin