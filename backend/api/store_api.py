# api/store_api.py — 门店管理接口
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database.database import get_db
from schemas.store_schema import (
    StoreResponse, StoreCreate, StoreUpdate,
    UserStoreCreate, UserStoreResponse, StoreUserResponse,
)
from crud import store_crud
from core import security
from models.user_model import User

router = APIRouter(tags=["门店管理 (Admin/Staff)"])


def _get_visible_store_ids(current_user: User, db: Session) -> Optional[List[int]]:
    """staff 用户返回其绑定的门店ID列表，admin 返回 None 表示全量"""
    if current_user.role == "admin":
        return None
    stores = store_crud.get_user_stores(db, current_user.id)
    return [s.id for s in stores]


# ==================== 门店 CRUD ====================

@router.get("/", response_model=List[StoreResponse])
def read_stores(
    search: Optional[str] = Query(None, description="按门店名称或编码搜索"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """获取门店列表。admin 查看全部，staff 仅查看绑定的门店"""
    security.require_admin_or_staff(current_user)

    if current_user.role == "admin":
        stores = store_crud.get_stores(db, skip=skip, limit=limit, search=search)
    else:
        user_store_ids = _get_visible_store_ids(current_user, db)
        if not user_store_ids:
            return []
        stores = db.query(store_crud.Store).filter(
            store_crud.Store.id.in_(user_store_ids)
        )
        if search:
            like = f"%{search}%"
            stores = stores.filter(
                (store_crud.Store.name.like(like)) | (store_crud.Store.code.like(like))
            )
        stores = stores.offset(skip).limit(limit).all()
    return stores


@router.post("/", response_model=StoreResponse, status_code=201)
def create_store(
    store: StoreCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """创建新门店（管理员）"""
    security.require_admin(current_user)
    try:
        return store_crud.create_store(db, store)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("/{store_id}", response_model=StoreResponse)
def read_store(
    store_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """获取门店详情"""
    security.require_admin_or_staff(current_user)
    store = store_crud.get_store_by_id(db, store_id)
    if not store:
        raise HTTPException(status_code=404, detail="门店不存在")
    # staff 只能查看自己绑定的门店
    if current_user.role == "staff":
        user_store_ids = _get_visible_store_ids(current_user, db)
        if store_id not in (user_store_ids or []):
            raise HTTPException(status_code=403, detail="无权查看该门店")
    return store


@router.put("/{store_id}", response_model=StoreResponse)
def update_store(
    store_id: int,
    store: StoreUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """更新门店信息（管理员）"""
    security.require_admin(current_user)
    try:
        updated = store_crud.update_store(db, store_id, store)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    if not updated:
        raise HTTPException(status_code=404, detail="门店不存在")
    return updated


@router.delete("/{store_id}")
def soft_delete_store(
    store_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """停用门店（管理员）"""
    security.require_admin(current_user)
    success = store_crud.soft_delete_store(db, store_id)
    if not success:
        raise HTTPException(status_code=404, detail="门店不存在")
    return {"detail": "门店已停用"}


# ==================== 用户-门店绑定 ====================

@router.post("/{store_id}/users", response_model=UserStoreResponse, status_code=201)
def bind_user_to_store_endpoint(
    store_id: int,
    data: UserStoreCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """将用户绑定到门店（管理员）"""
    security.require_admin(current_user)
    # 强制 data 中的 store_id 与路径一致
    data.store_id = store_id
    try:
        return store_crud.bind_user_to_store(db, data)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.delete("/{store_id}/users/{user_id}")
def unbind_user_from_store_endpoint(
    store_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """解除用户与门店的绑定（管理员）"""
    security.require_admin(current_user)
    success = store_crud.unbind_user_from_store(db, user_id, store_id)
    if not success:
        raise HTTPException(status_code=404, detail="未找到该绑定记录")
    return {"detail": "已解除绑定"}


@router.get("/{store_id}/users", response_model=List[StoreUserResponse])
def get_store_users_endpoint(
    store_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """获取门店下绑定的用户列表"""
    security.require_admin_or_staff(current_user)
    # 确认门店存在
    if not store_crud.get_store_by_id(db, store_id):
        raise HTTPException(status_code=404, detail="门店不存在")
    # staff 只能查看自己绑定的门店
    if current_user.role == "staff":
        user_store_ids = _get_visible_store_ids(current_user, db)
        if store_id not in (user_store_ids or []):
            raise HTTPException(status_code=403, detail="无权查看该门店用户")
    rows = store_crud.get_store_users(db, store_id)
    # 将元组 (UserStore, User) 转为 StoreUserResponse
    return [
        StoreUserResponse(
            user_id=us.user_id,
            store_id=us.store_id,
            is_primary=us.is_primary,
            nickname=u.nickname,
            role=u.role,
            position_desc=u.position_desc,
        )
        for us, u in rows
    ]
