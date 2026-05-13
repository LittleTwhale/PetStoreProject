# backend/crud/customer_crud.py
from sqlalchemy.orm import Session
from models.customer_model import CustomerProfile
from schemas.customer_schema import CustomerProfileCreate, CustomerProfileUpdate


def get_customers(db: Session, skip: int = 0, limit: int = 100, search: str | None = None,
                   store_id: int | None = None):
    """获取客户列表，支持分页、按姓名/电话搜索和门店过滤"""
    query = db.query(CustomerProfile)
    if search:
        like_pattern = f"%{search}%"
        query = query.filter(
            (CustomerProfile.real_name.like(like_pattern)) |
            (CustomerProfile.phone.like(like_pattern))
        )
    if store_id is not None:
        query = query.filter(CustomerProfile.store_id == store_id)
    return query.offset(skip).limit(limit).all()


def get_customer_by_id(db: Session, customer_id: int):
    """根据客户档案ID查询客户信息"""
    return db.query(CustomerProfile).filter(CustomerProfile.id == customer_id).first()


def get_customer_by_user_id(db: Session, user_id: int):
    """根据基础用户ID查询客户档案"""
    return db.query(CustomerProfile).filter(CustomerProfile.user_id == user_id).first()


def create_customer(db: Session, customer: CustomerProfileCreate):
    """创建客户档案，如 user_id 已被建档则抛出异常"""
    existing = db.query(CustomerProfile).filter(
        CustomerProfile.user_id == customer.user_id
    ).first()
    if existing:
        raise ValueError(f"用户ID {customer.user_id} 已关联客户档案，不允许重复建档")
    db_customer = CustomerProfile(**customer.model_dump())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


def update_customer(db: Session, customer_id: int, customer: CustomerProfileUpdate):
    """更新客户档案信息"""
    db_customer = get_customer_by_id(db, customer_id)
    if db_customer:
        update_data = customer.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_customer, key, value)
        db.commit()
        db.refresh(db_customer)
    return db_customer


def delete_customer(db: Session, customer_id: int) -> bool:
    """删除客户档案（关联的宠物 owner_id 会被置空）"""
    db_customer = get_customer_by_id(db, customer_id)
    if not db_customer:
        return False
    db.delete(db_customer)
    db.commit()
    return True
