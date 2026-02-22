# main.py
# 后端服务器入口
#

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src import logger
from src.router import api_router
from src.llm import offline
from src.utils import remove_os_environ_proxies

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    生命周期管理
    """

    # Startup
    logger.info("Starting backend server...")
    remove_os_environ_proxies() # 移除环境变量中的代理设置，防止影响本地服务调用

    logger.info("Starting offline chat models models...")
    offline.get_offline_chat_model() # 预加载离线聊天模型
    # offline.get_offline_reasoning_model() # 预加载离线推理模型
    logger.info("Offline models initialized.")  

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
