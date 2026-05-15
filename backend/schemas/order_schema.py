# schemas/order_schema.py — 订单管理 Schema
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


# ==================== 订单明细 ====================

class OrderItemBase(BaseModel):
    item_type: str
    product_id: Optional[int] = None
    service_id: Optional[int] = None
    quantity: int = 1
    unit_price: float
    subtotal: float
    staff_id: Optional[int] = None


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemUpdate(BaseModel):
    item_type: Optional[str] = None
    product_id: Optional[int] = None
    service_id: Optional[int] = None
    quantity: Optional[int] = None
    unit_price: Optional[float] = None
    subtotal: Optional[float] = None
    staff_id: Optional[int] = None


class OrderItemResponse(OrderItemBase):
    id: int
    order_id: int
    # 冗余显示字段
    product_name: Optional[str] = None
    service_name: Optional[str] = None
    staff_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ==================== 订单 ====================

class OrderBase(BaseModel):
    store_id: int
    order_type: str
    customer_id: Optional[int] = None
    total_amount: float = 0
    discount_amount: float = 0
    final_amount: float = 0
    payment_method: str = "cash"
    status: str = "pending"
    operator_id: Optional[int] = None
    remark: Optional[str] = None


class OrderCreate(BaseModel):
    store_id: int
    order_type: str
    customer_id: Optional[int] = None
    discount_amount: float = 0
    payment_method: str = "cash"
    operator_id: Optional[int] = None
    remark: Optional[str] = None
    items: List[OrderItemCreate]


class OrderUpdate(BaseModel):
    order_type: Optional[str] = None
    customer_id: Optional[int] = None
    total_amount: Optional[float] = None
    discount_amount: Optional[float] = None
    final_amount: Optional[float] = None
    payment_method: Optional[str] = None
    status: Optional[str] = None
    operator_id: Optional[int] = None
    remark: Optional[str] = None


class OrderResponse(BaseModel):
    id: int
    order_no: str
    store_id: int
    order_type: str
    customer_id: Optional[int] = None
    total_amount: float
    discount_amount: float
    final_amount: float
    payment_method: str
    status: str
    operator_id: Optional[int] = None
    remark: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    # 冗余显示字段
    customer_name: Optional[str] = None
    operator_name: Optional[str] = None
    store_name: Optional[str] = None
    items: List[OrderItemResponse] = []

    model_config = ConfigDict(from_attributes=True)


class OrderListResponse(BaseModel):
    id: int
    order_no: str
    store_id: int
    order_type: str
    customer_id: Optional[int] = None
    total_amount: float
    discount_amount: float
    final_amount: float
    payment_method: str
    status: str
    operator_id: Optional[int] = None
    remark: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    customer_name: Optional[str] = None
    operator_name: Optional[str] = None
    store_name: Optional[str] = None
    item_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class OrderStatusUpdate(BaseModel):
    status: str
    remark: Optional[str] = None
