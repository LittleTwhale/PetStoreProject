# main.py
import os

from fastapi import FastAPI, APIRouter
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from api.auth_api import router as auth_router

app = FastAPI(title="PetStore API", version="1.0.0")

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务（头像等）
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 创建一个总的 API 路由组
api_router = APIRouter(prefix="/api")

# 将各模块的路由注册到总路由下
api_router.include_router(auth_router, prefix="/auth")

# 将总路由注册到 app
app.include_router(api_router)
