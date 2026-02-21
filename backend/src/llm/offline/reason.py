# llm/offline/reason.py
# 本地 Reasoning Model
#

from llama_cpp import Llama

from src.config import general


offline_reasoning_model: Llama | None = None


def _build_offline_reasoning_model() -> None:
    """
    初始化离线推理模型

    这么做的原因是为了避免在模块导入时就加载模型，导致不必要的资源占用和潜在的性能问题。
    """

    global offline_reasoning_model

    offline_reasoning_model = Llama(
        model_path = general.OFFLINE_REASONING_MODEL_PATH.resolve().as_posix(),
        n_gpu_layers = 0, # 不使用 GPU 推理
        n_ctx = 4096, # 上下文长度
        n_threads = 3, # 每个模型3个线程 两个模型6个线程 剩下2个防止卡死
        chat_format = "chatml",
        verbose=False
    )


def get_offline_reasoning_model() -> Llama:
    """
    获取离线推理模型实例

    Returns:
        Llama: 离线推理模型实例
    """

    global offline_reasoning_model

    if offline_reasoning_model is None:
        _build_offline_reasoning_model()

    return offline_reasoning_model


__all__ = [
    "get_offline_reasoning_model",
]
