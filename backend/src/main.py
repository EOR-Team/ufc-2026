# main.py
# 后端服务器入口
#

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src import logger
from src.router import api_router
from src.llm import online, offline
from src.utils import remove_os_environ_proxies, check_network_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    生命周期管理
    """

    # Startup
    logger.info("Starting backend server...")
    remove_os_environ_proxies() # 移除环境变量中的代理设置，防止影响本地服务调用

    if not check_network_connection():
        # 如果没网 默认后面一直在离线模型运行 直接初始化离线模型
        logger.warning("No network connection detected. Defaulting to offline LLM models.")
        offline.get_offline_chat_model()
        offline.get_offline_reasoning_model()
    else:
        # 那就是有网 默认后面一直用在线模型 直接初始化在线模型
        logger.warning("Network connection detected. Using online LLM models.")
        online.get_online_chat_model()
        online.get_online_reasoning_model()

    yield 

    # Shutdown
    logger.info("Shutting down backend server...")


# 创建 FastAPI 应用
app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
