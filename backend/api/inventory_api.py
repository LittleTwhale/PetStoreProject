# api/inventory_api.py — 库存管理接口
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database.database import get_db
from schemas.inventory_schema import (
    InventoryCategoryResponse, InventoryCategoryCreate, InventoryCategoryUpdate,
    InventoryItemResponse, InventoryItemCreate, InventoryItemUpdate,
    InventoryLogResponse,
    StockInRequest, StockOutRequest,
)
from crud import inventory_crud
from models.inventory_model import InventoryCategory, InventoryItem, InventoryLog
from models.user_model import User
from core import security

router = APIRouter(tags=["库存管理 (Admin/Staff)"])


# ==================== 库存分类 ====================

@router.get("/categories/", response_model=List[InventoryCategoryResponse])
def read_categories(
    store_id: Optional[int] = Query(None, description="按门店过滤"),
    search: Optional[str] = Query(None, description="按名称搜索"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """获取库存分类列表"""
    security.require_admin_or_staff(current_user)
    return inventory_crud.get_categories(db, store_id=store_id, skip=skip, limit=limit, search=search)


@router.post("/categories/", response_model=InventoryCategoryResponse, status_code=201)
def create_category(
    category: InventoryCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """创建库存分类（管理员）"""
    security.require_admin(current_user)
    return inventory_crud.create_category(db, category)


@router.put("/categories/{category_id}", response_model=InventoryCategoryResponse)
def update_category(
    category_id: int,
    category: InventoryCategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """更新库存分类（管理员）"""
    security.require_admin(current_user)
    updated = inventory_crud.update_category(db, category_id, category)
    if not updated:
        raise HTTPException(status_code=404, detail="分类不存在")
    return updated


@router.delete("/categories/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """停用库存分类（管理员）"""
    security.require_admin(current_user)
    success = inventory_crud.soft_delete_category(db, category_id)
    if not success:
        raise HTTPException(status_code=404, detail="分类不存在")
    return {"detail": "分类已停用"}


# ==================== 库存物品 ====================

@router.get("/items/", response_model=List[InventoryItemResponse])
def read_items(
    store_id: Optional[int] = Query(None, description="按门店过滤"),
    category_id: Optional[int] = Query(None, description="按分类过滤"),
    search: Optional[str] = Query(None, description="按名称/SKU搜索"),
    low_stock_only: bool = Query(False, description="仅显示低库存物品"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """获取库存物品列表"""
    security.require_admin_or_staff(current_user)
    items = inventory_crud.get_items(
        db, store_id=store_id, category_id=category_id,
        search=search, low_stock_only=low_stock_only,
        skip=skip, limit=limit,
    )
    # 补充分类名称
    result = []
    for item in items:
        item_dict = {
            "id": item.id, "category_id": item.category_id, "store_id": item.store_id,
            "name": item.name, "sku": item.sku, "unit": item.unit,
            "quantity": item.quantity, "safety_stock": item.safety_stock,
            "unit_price": item.unit_price, "selling_price": item.selling_price,
            "supplier": item.supplier, "is_active": item.is_active,
            "created_at": item.created_at, "updated_at": item.updated_at,
            "category_name": item.category.name if item.category else None,
        }
        result.append(InventoryItemResponse(**item_dict))
    return result


@router.post("/items/", response_model=InventoryItemResponse, status_code=201)
def create_item(
    item: InventoryItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """创建库存物品"""
    security.require_admin_or_staff(current_user)
    try:
        return inventory_crud.create_item(db, item)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("/items/{item_id}", response_model=InventoryItemResponse)
def read_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """获取物品详情"""
    security.require_admin_or_staff(current_user)
    item = inventory_crud.get_item_by_id(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="物品不存在")
    return item


@router.put("/items/{item_id}", response_model=InventoryItemResponse)
def update_item(
    item_id: int,
    item: InventoryItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """更新物品信息"""
    security.require_admin_or_staff(current_user)
    try:
        updated = inventory_crud.update_item(db, item_id, item)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    if not updated:
        raise HTTPException(status_code=404, detail="物品不存在")
    return updated


@router.delete("/items/{item_id}")
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """停用物品（管理员）"""
    security.require_admin(current_user)
    success = inventory_crud.soft_delete_item(db, item_id)
    if not success:
        raise HTTPException(status_code=404, detail="物品不存在")
    return {"detail": "物品已停用"}


# ==================== 出入库操作 ====================

@router.post("/items/stock-in", response_model=InventoryItemResponse)
def stock_in_endpoint(
    req: StockInRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """入库操作"""
    security.require_admin_or_staff(current_user)
    try:
        return inventory_crud.stock_in(
            db, item_id=req.item_id, quantity=req.quantity,
            operator_id=current_user.id, unit_price=req.unit_price,
            remark=req.remark,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/items/stock-out", response_model=InventoryItemResponse)
def stock_out_endpoint(
    req: StockOutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """出库操作"""
    security.require_admin_or_staff(current_user)
    try:
        return inventory_crud.stock_out(
            db, item_id=req.item_id, quantity=req.quantity,
            operator_id=current_user.id, remark=req.remark,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== 库存流水 ====================

@router.get("/logs/", response_model=List[InventoryLogResponse])
def read_logs(
    store_id: Optional[int] = Query(None, description="按门店过滤"),
    item_id: Optional[int] = Query(None, description="按物品过滤"),
    change_type: Optional[str] = Query(None, description="变动类型: in/out/adjust"),
    operator_id: Optional[int] = Query(None, description="按操作人过滤"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """查询库存流水日志"""
    security.require_admin_or_staff(current_user)
    logs = inventory_crud.get_logs(
        db, store_id=store_id, item_id=item_id, change_type=change_type,
        operator_id=operator_id, start_time=start_time, end_time=end_time,
        skip=skip, limit=limit,
    )
    result = []
    for log in logs:
        item = log.item
        result.append(InventoryLogResponse(
            id=log.id, item_id=log.item_id, store_id=log.store_id,
            change_type=log.change_type, quantity_change=log.quantity_change,
            quantity_after=log.quantity_after, operator_id=log.operator_id,
            remark=log.remark, created_at=log.created_at,
            item_name=item.name if item else None,
            item_sku=item.sku if item else None,
        ))
    return result
