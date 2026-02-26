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
from src.voice_interaction.voice_interaction import VoiceInteraction

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    生命周期管理
    """

    # Startup
    logger.info("Starting backend server...")

    # === 1. 网络设置 ===
    remove_os_environ_proxies() # 移除环境变量中的代理设置，防止影响本地服务调用

    # === 2. 语言模型预热 ===
    logger.info("Starting offline chat models models...")
    offline.get_offline_chat_model() # 预加载离线聊天模型
    # offline.get_offline_reasoning_model() # 预加载离线推理模型
    logger.info("Offline chat models initialized.")  

    # === 3. 语音交互预热 ===
    await VoiceInteraction().warmup()

    yield 

    # Shutdown
    logger.info("Shutting down backend server...")


# 创建 FastAPI 应用
app = FastAPI(lifespan=lifespan)

# 配置 CORS 中间件，解决前端跨域访问问题
# 重要：必须在 include_router 之前添加中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，开发环境使用
    allow_credentials=True,  # 允许携带认证信息
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
    expose_headers=["*"],  # 暴露所有响应头给前端
    max_age=600,  # 预检请求缓存时间（秒）
)

app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
