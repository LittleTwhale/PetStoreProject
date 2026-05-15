# schemas/dashboard_schema.py — 数据面板 Schema
from pydantic import BaseModel
from typing import Optional


class StatCard(BaseModel):
    """统计卡片数据"""
    label: str
    value: float
    unit: str = ""
    icon: str = ""


class DailyTrend(BaseModel):
    """每日趋势"""
    date: str
    order_count: int = 0
    revenue: float = 0


class InventoryAlert(BaseModel):
    """库存预警"""
    id: int
    name: str
    sku: str
    quantity: int
    safety_stock: int
    unit: str


class TopItem(BaseModel):
    """热门项目"""
    id: int
    name: str
    count: int
    revenue: float


class RecentOrder(BaseModel):
    """最近订单摘要"""
    id: int
    order_no: str
    order_type: str
    final_amount: float
    status: str
    customer_name: Optional[str] = None
    created_at: str


class DashboardResponse(BaseModel):
    """数据面板完整响应"""
    today_revenue: float = 0
    today_orders: int = 0
    month_revenue: float = 0
    month_orders: int = 0
    pending_orders: int = 0
    low_stock_count: int = 0
    daily_trend: list[DailyTrend] = []
    inventory_alerts: list[InventoryAlert] = []
    top_products: list[TopItem] = []
    top_services: list[TopItem] = []
    recent_orders: list[RecentOrder] = []
