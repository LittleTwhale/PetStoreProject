# schemas/pet_schema.py
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date


class PetBase(BaseModel):
    """宠物基础字段（创建时用）"""
    name: Optional[str] = None
    species: str  # 创建时必须指定物种
    breed: Optional[str] = None
    gender: Optional[str] = None
    weight: Optional[float] = None
    birth_date: Optional[date] = None
    is_neutered: Optional[bool] = False
    vaccine_status: Optional[str] = None
    avatar: Optional[str] = None
    special_notes: Optional[str] = None

    # 归属与价格
    ownership_type: str = "customer"  # customer, for_sale, store_mascot
    price: Optional[float] = None


class PetCreate(PetBase):
    """创建宠物时，owner_id 可选（店内宠物不需要主人）"""
    owner_id: Optional[int] = None


class PetUpdate(BaseModel):
    """更新宠物信息，所有字段可选（只更新传了的字段）"""
    name: Optional[str] = None
    species: Optional[str] = None
    breed: Optional[str] = None
    gender: Optional[str] = None
    weight: Optional[float] = None
    birth_date: Optional[date] = None
    is_neutered: Optional[bool] = None
    vaccine_status: Optional[str] = None
    avatar: Optional[str] = None
    special_notes: Optional[str] = None
    ownership_type: Optional[str] = None
    price: Optional[float] = None
    owner_id: Optional[int] = None


class PetResponse(PetBase):
    """返回宠物信息（含ID和主人ID）"""
    id: int
    owner_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
