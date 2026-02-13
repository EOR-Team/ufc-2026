# llm/offline/model.py
# 本地 Model
#

from llama_cpp import Llama

from src.config import general


offline_chat_model = Llama(
    model_path = general.OFFLINE_CHAT_MODEL_PATH.resolve().as_posix(),
    n_gpu_layers = 0, # 不使用 GPU 推理
    n_ctx = 2048, # 上下文长度
    n_threads = 3, # 每个模型3个线程 两个模型6个线程 剩下2个防止卡死
    chat_format = "chatml",
)

offline_reasoning_model = Llama(
    model_path = general.OFFLINE_REASONING_MODEL_PATH.resolve().as_posix(),
    n_gpu_layers = 0, # 不使用 GPU 推理
    n_ctx = 2048, # 上下文长度
    n_threads = 3, # 每个模型3个线程 两个模型6个线程 剩下2个防止卡死
    chat_format = "chatml",
)


