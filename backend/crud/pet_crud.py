# crud/pet_crud.py
from sqlalchemy.orm import Session
from models.pet_model import Pet
from schemas.pet_schema import PetCreate, PetUpdate
from typing import Optional


def get_pets(
    db: Session,
    ownership_type: Optional[str] = None,
    owner_id: Optional[int] = None,
    store_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
):
    """获取宠物列表，支持按归属类型、主人ID和门店过滤"""
    query = db.query(Pet)
    if ownership_type:
        query = query.filter(Pet.ownership_type == ownership_type)
    if owner_id is not None:
        query = query.filter(Pet.owner_id == owner_id)
    if store_id is not None:
        query = query.filter(Pet.store_id == store_id)
    return query.offset(skip).limit(limit).all()


def get_pet_by_id(db: Session, pet_id: int):
    """根据ID获取单个宠物档案"""
    return db.query(Pet).filter(Pet.id == pet_id).first()


def create_pet(db: Session, pet: PetCreate):
    """创建宠物档案"""
    db_pet = Pet(**pet.model_dump())
    db.add(db_pet)
    db.commit()
    db.refresh(db_pet)
    return db_pet


def update_pet(db: Session, pet_id: int, pet_update: PetUpdate):
    """更新宠物档案信息"""
    db_pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if db_pet:
        update_data = pet_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_pet, key, value)
        db.commit()
        db.refresh(db_pet)
    return db_pet


def delete_pet(db: Session, pet_id: int) -> bool:
    """删除宠物档案"""
    db_pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not db_pet:
        return False
    db.delete(db_pet)
    db.commit()
    return True
