# schemas/inventory_schema.py — 库存管理 Schema
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


# ==================== 库存分类 ====================

class InventoryCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    store_id: int


class InventoryCategoryCreate(InventoryCategoryBase):
    pass


class InventoryCategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class InventoryCategoryResponse(InventoryCategoryBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==================== 库存物品 ====================

class InventoryItemBase(BaseModel):
    category_id: int
    store_id: int
    name: str
    sku: str
    unit: str = "个"
    quantity: float = 0
    safety_stock: float = 0
    unit_price: Optional[float] = None
    selling_price: Optional[float] = None
    supplier: Optional[str] = None


class InventoryItemCreate(InventoryItemBase):
    pass


class InventoryItemUpdate(BaseModel):
    category_id: Optional[int] = None
    name: Optional[str] = None
    sku: Optional[str] = None
    unit: Optional[str] = None
    safety_stock: Optional[float] = None
    unit_price: Optional[float] = None
    selling_price: Optional[float] = None
    supplier: Optional[str] = None
    is_active: Optional[bool] = None


class InventoryItemResponse(InventoryItemBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    category_name: Optional[str] = None  # 冗余显示

    model_config = ConfigDict(from_attributes=True)


# ==================== 出入库请求 ====================

class StockInRequest(BaseModel):
    item_id: int
    quantity: float
    unit_price: Optional[float] = None
    remark: Optional[str] = None


class StockOutRequest(BaseModel):
    item_id: int
    quantity: float
    remark: Optional[str] = None


# ==================== 库存流水 ====================

class InventoryLogResponse(BaseModel):
    id: int
    item_id: int
    store_id: int
    change_type: str
    quantity_change: float
    quantity_after: float
    operator_id: Optional[int] = None
    remark: Optional[str] = None
    created_at: datetime
    item_name: Optional[str] = None
    item_sku: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
