# api/pet_api.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database.database import get_db
from schemas.pet_schema import PetResponse, PetCreate, PetUpdate
from crud import pet_crud
from core import security
from models.user_model import User

router = APIRouter(tags=["宠物台账管理 (Admin/Staff)"])

# 合法的归属类型
VALID_OWNERSHIP_TYPES = {"customer", "for_sale", "store_mascot"}


@router.get("/", response_model=List[PetResponse])
def read_pets(
    ownership_type: Optional[str] = Query(None, description="过滤归属类型: customer / for_sale / store_mascot"),
    owner_id: Optional[int] = Query(None, description="按主人ID过滤（查看某客户名下全部宠物）"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """获取宠物列表，支持按归属类型和主人ID过滤"""
    security.require_admin_or_staff(current_user)
    pets = pet_crud.get_pets(db, ownership_type=ownership_type, owner_id=owner_id, skip=skip, limit=limit)
    return pets


@router.get("/{pet_id}", response_model=PetResponse)
def read_pet(
    pet_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """获取单个宠物档案详情"""
    security.require_admin_or_staff(current_user)
    pet = pet_crud.get_pet_by_id(db, pet_id)
    if pet is None:
        raise HTTPException(status_code=404, detail="宠物档案不存在")
    return pet


@router.post("/", response_model=PetResponse, status_code=201)
def create_new_pet(
    pet: PetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """
    录入新宠物档案。
    - 客宠：传 owner_id，ownership_type 为 "customer"
    - 待售：不传 owner_id，ownership_type 为 "for_sale"，可选填 price
    - 店宠：不传 owner_id，ownership_type 为 "store_mascot"
    """
    security.require_admin_or_staff(current_user)

    # 校验归属类型合法性
    if pet.ownership_type not in VALID_OWNERSHIP_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"无效的归属类型，必须为: {', '.join(sorted(VALID_OWNERSHIP_TYPES))}",
        )

    # 客宠必须有主人
    if pet.ownership_type == "customer" and pet.owner_id is None:
        raise HTTPException(status_code=400, detail="客宠必须指定 owner_id")

    return pet_crud.create_pet(db, pet)


@router.put("/{pet_id}", response_model=PetResponse)
def update_existing_pet(
    pet_id: int,
    pet: PetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """
    修改宠物信息 / 宠物售出操作。
    售出场景：将 ownership_type 改为 "customer"，并绑定新的 owner_id。
    """
    security.require_admin_or_staff(current_user)

    # 校验归属类型（如果传了的话）
    update_data = pet.model_dump(exclude_unset=True)
    if "ownership_type" in update_data and update_data["ownership_type"] not in VALID_OWNERSHIP_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"无效的归属类型，必须为: {', '.join(sorted(VALID_OWNERSHIP_TYPES))}",
        )

    # 如果要将宠物变为客宠，必须同时提供 owner_id
    current_pet = pet_crud.get_pet_by_id(db, pet_id)
    if current_pet is None:
        raise HTTPException(status_code=404, detail="宠物档案不存在")

    new_ownership = update_data.get("ownership_type", current_pet.ownership_type)
    new_owner_id = update_data.get("owner_id", current_pet.owner_id)
    if new_ownership == "customer" and new_owner_id is None:
        raise HTTPException(status_code=400, detail="客宠必须指定 owner_id")

    updated_pet = pet_crud.update_pet(db, pet_id, pet)
    return updated_pet


@router.delete("/{pet_id}")
def delete_pet(
    pet_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user),
):
    """删除宠物档案"""
    security.require_admin_or_staff(current_user)
    success = pet_crud.delete_pet(db, pet_id)
    if not success:
        raise HTTPException(status_code=404, detail="宠物档案不存在")
    return {"detail": "宠物档案已删除"}
