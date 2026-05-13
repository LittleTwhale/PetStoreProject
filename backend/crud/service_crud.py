# crud/service_crud.py — 服务项目管理业务逻辑
from sqlalchemy.orm import Session

from models.service_model import Service
from schemas.service_schema import ServiceCreate, ServiceUpdate


# ==================== 服务项目 CRUD ====================

def get_services(db: Session, store_id: int | None = None,
                 category: str | None = None,
                 search: str | None = None,
                 skip: int = 0, limit: int = 100):
    """获取服务项目列表，支持按门店/分类/关键词过滤"""
    query = db.query(Service)
    if store_id is not None:
        query = query.filter(Service.store_id == store_id)
    if category:
        query = query.filter(Service.category == category)
    if search:
        like = f"%{search}%"
        query = query.filter(Service.name.like(like))
    return query.order_by(Service.category, Service.name).offset(skip).limit(limit).all()


def get_service_by_id(db: Session, service_id: int):
    return db.query(Service).filter(Service.id == service_id).first()


def create_service(db: Session, service: ServiceCreate):
    db_service = Service(**service.model_dump())
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service


def update_service(db: Session, service_id: int, service: ServiceUpdate):
    db_service = get_service_by_id(db, service_id)
    if db_service:
        update_data = service.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_service, key, value)
        db.commit()
        db.refresh(db_service)
    return db_service


def soft_delete_service(db: Session, service_id: int) -> bool:
    db_service = get_service_by_id(db, service_id)
    if not db_service:
        return False
    db_service.is_active = False
    db.commit()
    return True
