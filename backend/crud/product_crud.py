# crud/product_crud.py — 商品管理业务逻辑
from sqlalchemy.orm import Session, joinedload

from models.product_model import Product
from schemas.product_schema import ProductCreate, ProductUpdate


# ==================== 商品 CRUD ====================

def get_products(db: Session, store_id: int | None = None,
                 product_type: str | None = None,
                 search: str | None = None,
                 skip: int = 0, limit: int = 100):
    """获取商品列表，支持按门店/类型/关键词过滤"""
    query = db.query(Product)
    if store_id is not None:
        query = query.filter(Product.store_id == store_id)
    if product_type:
        query = query.filter(Product.product_type == product_type)
    if search:
        like = f"%{search}%"
        query = query.filter(Product.name.like(like))
    return query.order_by(Product.created_at.desc()).offset(skip).limit(limit).all()


def get_product_by_id(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()


def create_product(db: Session, product: ProductCreate):
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(db: Session, product_id: int, product: ProductUpdate):
    db_product = get_product_by_id(db, product_id)
    if db_product:
        update_data = product.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_product, key, value)
        db.commit()
        db.refresh(db_product)
    return db_product


def soft_delete_product(db: Session, product_id: int) -> bool:
    db_product = get_product_by_id(db, product_id)
    if not db_product:
        return False
    db_product.is_active = False
    db.commit()
    return True
