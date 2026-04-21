# schemas/auth_schema.py
from pydantic import BaseModel, Field

# 接收前端登录请求的格式
class LoginReq(BaseModel):
    identifier: str = Field(..., description="账号/手机号/邮箱")
    password: str = Field(..., description="明文密码")

# 返回给前端的 Token 格式
class TokenRes(BaseModel):
    access_token: str
    token_type: str = "bearer"