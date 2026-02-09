# main.py
# 后端服务器入口
#

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from src.llm.offline import server
from src import logger
from src.router import api_router
from src.utils import remove_os_environ_proxies
remove_os_environ_proxies() # 移除环境变量中的代理设置，防止影响本地服务调用


# 创建 FastAPI 应用
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def app_on_startup():
    server.start_local_llm_server()
    logger.info("本地 LLM 服务已启动")

@app.on_event("shutdown")
def app_on_shutdown():
    server.stop_local_llm_server()
    logger.info("本地 LLM 服务已停止")

app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)