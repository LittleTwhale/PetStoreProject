# schemas/auth_schema.py
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# ==================== 登录 ====================
class LoginReq(BaseModel):
    identifier: str = Field(..., description="账号/手机号/邮箱")
    password: str = Field(..., description="明文密码")


class TokenRes(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ==================== 注册 ====================
class RegisterReq(BaseModel):
    identifier: str = Field(..., min_length=3, max_length=100, description="账号/手机号/邮箱")
    password: str = Field(..., min_length=6, max_length=100, description="明文密码(至少6位)")
    nickname: str = Field(default="神秘宠友", max_length=50, description="昵称")


# ==================== 用户信息 ====================
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


class UserUpdateReq(BaseModel):
    nickname: str | None = Field(None, max_length=50, description="昵称")
    position_desc: str | None = Field(None, max_length=100, description="职位/身份描述")


# ==================== 管理员 ====================
class AdminCreateUserReq(BaseModel):
    identifier: str = Field(..., min_length=3, max_length=100, description="账号")
    password: str = Field(..., min_length=6, max_length=100, description="密码(至少6位)")
    nickname: str = Field(default="神秘宠友", max_length=50, description="昵称")
    role: str = Field(default="customer", description="角色: admin/staff/customer")
    position_desc: str | None = Field(None, max_length=100, description="职位描述")


class AdminUpdateUserReq(BaseModel):
    nickname: str | None = Field(None, max_length=50)
    role: str | None = Field(None, description="角色")
    position_desc: str | None = Field(None, max_length=100)
    is_active: bool | None = Field(None, description="是否激活")
    permissions: Any | None = Field(None, description="权限列表")


class UserListItem(BaseModel):
    id: int
    nickname: str
    avatar: str | None
    role: str
    position_desc: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AvatarRes(BaseModel):
    avatar_url: str
