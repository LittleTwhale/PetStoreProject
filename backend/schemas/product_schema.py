# schemas/product_schema.py — 商品管理 Schema
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


# ==================== 商品 ====================

class ProductBase(BaseModel):
    store_id: int
    name: str
    product_type: str = "goods"
    pet_id: Optional[int] = None
    inventory_item_id: Optional[int] = None
    price: float = 0
    cost_price: Optional[float] = None
    stock: int = 0
    description: Optional[str] = None
    cover_image: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    store_id: Optional[int] = None
    name: Optional[str] = None
    product_type: Optional[str] = None
    pet_id: Optional[int] = None
    inventory_item_id: Optional[int] = None
    price: Optional[float] = None
    cost_price: Optional[float] = None
    stock: Optional[int] = None
    description: Optional[str] = None
    cover_image: Optional[str] = None
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    # 冗余显示字段
    pet_name: Optional[str] = None
    inventory_item_name: Optional[str] = None
    store_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
