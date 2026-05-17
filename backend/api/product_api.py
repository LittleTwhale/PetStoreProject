# api/product_api.py — 商品管理接口
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional

from database.database import get_db
from schemas.product_schema import ProductResponse, ProductCreate, ProductUpdate
from crud import product_crud
from models.product_model import Product
from models.user_model import User
from core import security
from upload_utils import save_upload_image

router = APIRouter(tags=["商品管理"])


# ==================== 商品图片上传 ====================

@router.post("/upload-cover")
def upload_product_cover(
    file: UploadFile = File(...),
    current_user: User = Depends(security.get_current_user),
):
    """上传商品封面图，返回图片 URL"""
    security.require_admin_or_staff(current_user)
    url = save_upload_image(file, "products")
    return {"url": url}


# ==================== 商品 CRUD ====================

@router.get("/", response_model=List[ProductResponse])
def read_products(
    store_id: Optional[int] = Query(None, description="按门店过滤"),
    product_type: Optional[str] = Query(None, description="类型: goods / pet"),
    search: Optional[str] = Query(None, description="按名称搜索"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """获取商品列表"""
    security.require_admin_or_staff(current_user)
    items = product_crud.get_products(
        db, store_id=store_id, product_type=product_type,
        search=search, skip=skip, limit=limit,
    )
    result = []
    for p in items:
        result.append(ProductResponse(
            id=p.id, store_id=p.store_id, name=p.name,
            product_type=p.product_type, pet_id=p.pet_id,
            inventory_item_id=p.inventory_item_id,
            price=p.price, cost_price=p.cost_price,
            stock=p.stock, description=p.description,
            cover_image=p.cover_image, is_active=p.is_active,
            created_at=p.created_at, updated_at=p.updated_at,
            pet_name=p.pet.name if p.pet else None,
            inventory_item_name=p.inventory_item.name if p.inventory_item else None,
            store_name=None,
        ))
    return result


@router.post("/", response_model=ProductResponse, status_code=201)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """创建商品"""
    security.require_admin_or_staff(current_user)
    return product_crud.create_product(db, product)


@router.get("/{product_id}", response_model=ProductResponse)
def read_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """获取商品详情"""
    security.require_admin_or_staff(current_user)
    p = product_crud.get_product_by_id(db, product_id)
    if not p:
        raise HTTPException(status_code=404, detail="商品不存在")
    return ProductResponse(
        id=p.id, store_id=p.store_id, name=p.name,
        product_type=p.product_type, pet_id=p.pet_id,
        inventory_item_id=p.inventory_item_id,
        price=p.price, cost_price=p.cost_price,
        stock=p.stock, description=p.description,
        cover_image=p.cover_image, is_active=p.is_active,
        created_at=p.created_at, updated_at=p.updated_at,
        pet_name=p.pet.name if p.pet else None,
        inventory_item_name=p.inventory_item.name if p.inventory_item else None,
        store_name=None,
    )


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """更新商品信息"""
    security.require_admin_or_staff(current_user)
    updated = product_crud.update_product(db, product_id, product)
    if not updated:
        raise HTTPException(status_code=404, detail="商品不存在")
    return updated


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """下架商品"""
    security.require_admin_or_staff(current_user)
    success = product_crud.soft_delete_product(db, product_id)
    if not success:
        raise HTTPException(status_code=404, detail="商品不存在")
    return {"detail": "商品已下架"}
