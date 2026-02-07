# main.py
# 后端服务器入口
#

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from src.llm.local import server


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
    print("本地 LLM 服务已启动")

@app.on_event("shutdown")
def app_on_shutdown():
    server.stop_local_llm_server()
    print("本地 LLM 服务已停止")


root_router = APIRouter(prefix="/api")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
