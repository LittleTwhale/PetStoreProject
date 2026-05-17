# api/service_api.py — 服务项目管理接口
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database.database import get_db
from schemas.service_schema import ServiceResponse, ServiceCreate, ServiceUpdate
from crud import service_crud
from models.service_model import Service
from models.user_model import User
from core import security

router = APIRouter(tags=["服务管理"])


# ==================== 服务项目 CRUD ====================

@router.get("/", response_model=List[ServiceResponse])
def read_services(
    store_id: Optional[int] = Query(None, description="按门店过滤"),
    category: Optional[str] = Query(None, description="分类: grooming/boarding/medical/training/other"),
    search: Optional[str] = Query(None, description="按名称搜索"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """获取服务项目列表。admin可查看全部或指定门店，staff仅能查看绑定门店的服务"""
    security.require_admin_or_staff(current_user)
    effective_store_id = security.get_effective_store_id(current_user, store_id, db)
    return service_crud.get_services(
        db, store_id=effective_store_id, category=category,
        search=search, skip=skip, limit=limit,
    )


@router.post("/", response_model=ServiceResponse, status_code=201)
def create_service(
    service: ServiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """创建服务项目（管理员）"""
    security.require_admin(current_user)
    return service_crud.create_service(db, service)


@router.get("/{service_id}", response_model=ServiceResponse)
def read_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """获取服务项目详情"""
    security.require_admin_or_staff(current_user)
    s = service_crud.get_service_by_id(db, service_id)
    if not s:
        raise HTTPException(status_code=404, detail="服务项目不存在")
    return s


@router.put("/{service_id}", response_model=ServiceResponse)
def update_service(
    service_id: int,
    service: ServiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """更新服务项目（管理员）"""
    security.require_admin(current_user)
    updated = service_crud.update_service(db, service_id, service)
    if not updated:
        raise HTTPException(status_code=404, detail="服务项目不存在")
    return updated


@router.delete("/{service_id}")
def delete_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """下架服务项目（管理员）"""
    security.require_admin(current_user)
    success = service_crud.soft_delete_service(db, service_id)
    if not success:
        raise HTTPException(status_code=404, detail="服务项目不存在")
    return {"detail": "服务项目已下架"}
