# api/dashboard_api.py — 数据面板接口
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from database.database import get_db
from schemas.dashboard_schema import DashboardResponse
from crud import dashboard_crud
from models.user_model import User
from core import security

router = APIRouter(tags=["数据面板"])


@router.get("/summary", response_model=DashboardResponse)
def get_dashboard_summary(
    store_id: Optional[int] = Query(None, description="按门店过滤（管理员可选）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """获取数据面板聚合数据。admin可查看全部或指定门店，staff仅能查看绑定门店的数据"""
    security.require_admin_or_staff(current_user)
    effective_store_id = security.get_effective_store_id(current_user, store_id, db)
    data = dashboard_crud.get_dashboard_data(db, store_id=effective_store_id)
    return DashboardResponse(**data)
