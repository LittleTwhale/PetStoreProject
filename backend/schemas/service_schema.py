# schemas/service_schema.py — 服务项目管理 Schema
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


# ==================== 服务项目 ====================

class ServiceBase(BaseModel):
    store_id: int
    name: str
    category: str = "other"
    price: float = 0
    duration_minutes: int = 0
    description: Optional[str] = None


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    store_id: Optional[int] = None
    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    duration_minutes: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ServiceResponse(ServiceBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    store_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
