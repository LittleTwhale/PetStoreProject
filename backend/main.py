# main.py
from fastapi import FastAPI, APIRouter
from api.auth_api import router as auth_router

app = FastAPI(title="PetStore API", version="1.0.0")

# 创建一个总的 API 路由组
api_router = APIRouter(prefix="/api")

# 将各模块的路由注册到总路由下
api_router.include_router(auth_router, prefix="/auth")

# 将总路由注册到 app
app.include_router(api_router)