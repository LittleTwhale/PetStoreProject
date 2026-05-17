# api/customer_api.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database.database import get_db
from schemas.customer_schema import CustomerProfileResponse, CustomerProfileCreate, CustomerProfileUpdate
from crud import customer_crud
from core import security
from models.user_model import User

router = APIRouter(tags=["客户档案管理 (Admin/Staff)"])


@router.get("/", response_model=List[CustomerProfileResponse])
def read_customers(
    search: Optional[str] = Query(None, description="按客户姓名或电话模糊搜索"),
    store_id: Optional[int] = Query(None, description="按门店ID过滤（可选，顾客不强制绑定门店）"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """获取客户列表（包含名下宠物）。顾客不绑定门店，admin/staff 均可查看全部客户"""
    security.require_admin_or_staff(current_user)
    # 顾客可能去不同门店，不强制按门店过滤；store_id 参数直接透传
    customers = customer_crud.get_customers(db, skip=skip, limit=limit, search=search, store_id=store_id)
    return customers


@router.get("/{customer_id}", response_model=CustomerProfileResponse)
def read_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """获取单一客户详情（包含名下宠物）"""
    security.require_admin_or_staff(current_user)
    customer = customer_crud.get_customer_by_id(db, customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="客户档案不存在")
    return customer


@router.post("/", response_model=CustomerProfileResponse, status_code=201)
def create_new_customer(
    customer: CustomerProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """后台直接建档新客户。顾客不强制绑定门店，store_id 可选"""
    security.require_admin_or_staff(current_user)
    try:
        return customer_crud.create_customer(db, customer)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.put("/{customer_id}", response_model=CustomerProfileResponse)
def update_existing_customer(
    customer_id: int,
    customer: CustomerProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """后台修改客户资料。顾客不绑定门店，admin/staff 均可修改"""
    security.require_admin_or_staff(current_user)
    existing = customer_crud.get_customer_by_id(db, customer_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="客户档案不存在")
    updated_customer = customer_crud.update_customer(db, customer_id, customer)
    return updated_customer


@router.delete("/{customer_id}")
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """删除客户档案。顾客不绑定门店，admin/staff 均可删除"""
    security.require_admin_or_staff(current_user)
    customer = customer_crud.get_customer_by_id(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="客户档案不存在")
    pet_count = len(customer.pets) if customer.pets else 0
    success = customer_crud.delete_customer(db, customer_id)
    if not success:
        raise HTTPException(status_code=404, detail="客户档案不存在")
    if pet_count > 0:
        return {"detail": f"客户档案已删除，{pet_count} 只宠物已解除归属（owner_id 置空）"}
    return {"detail": "客户档案已删除"}
