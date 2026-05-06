# schemas/auth_schema.py
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

# 接收前端登录请求的格式
class LoginReq(BaseModel):
    identifier: str = Field(..., description="账号/手机号/邮箱")
    password: str = Field(..., description="明文密码")

# 返回给前端的 Token 格式
class TokenRes(BaseModel):
    access_token: str
    token_type: str = "bearer"

# 返回给前端的当前用户信息格式
class UserInfo(BaseModel):
    id: int
    nickname: str
    avatar: str | None
    role: str
    position_desc: str | None
    permissions: Any | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}