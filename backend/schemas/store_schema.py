# schemas/store_schema.py — 门店管理 Schema
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class StoreBase(BaseModel):
    name: str
    code: str
    address: Optional[str] = None
    phone: Optional[str] = None
    manager_id: Optional[int] = None


class StoreCreate(StoreBase):
    pass


class StoreUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    manager_id: Optional[int] = None
    is_active: Optional[bool] = None


class StoreResponse(StoreBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---- 用户-门店绑定 ----
class UserStoreBase(BaseModel):
    user_id: int
    store_id: int
    is_primary: bool = False


class UserStoreCreate(UserStoreBase):
    pass


class UserStoreResponse(UserStoreBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StoreUserResponse(BaseModel):
    """门店绑定的用户信息（含用户详情）"""
    user_id: int
    store_id: int
    is_primary: bool
    nickname: str
    role: str
    position_desc: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
