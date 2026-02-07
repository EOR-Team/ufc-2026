# utils.py
# 一些工具

import gson
from src.config import OFFLINE_MODEL_TYPES, OFFLINE_MODEL_DIR


def convert_model_name_to_path(model: OFFLINE_MODEL_TYPES) -> str:
    """
    将模型名称转换为模型文件路径

    Args:
        model_name (OFFLINE_MODEL_TYPES): 模型名称

    Returns:
        str: 模型文件路径
    """

    with open(OFFLINE_MODEL_DIR / "mapping.json", "r", encoding="utf-8") as f:
        model_mapping: dict[str, str] = gson.loads(f.read())
    
    if model not in model_mapping:
        return ""
    
    model_filename = model_mapping[model]
    model_path = OFFLINE_MODEL_DIR / model_filename

    return model_path.resolve().as_posix()
