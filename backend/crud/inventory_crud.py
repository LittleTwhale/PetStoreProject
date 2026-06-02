# crud/inventory_crud.py — 库存管理业务逻辑
from sqlalchemy.orm import Session
from datetime import datetime

from models.inventory_model import InventoryCategory, InventoryItem, InventoryLog
from schemas.inventory_schema import (
    InventoryCategoryCreate, InventoryCategoryUpdate,
    InventoryItemCreate, InventoryItemUpdate,
)


# ==================== 分类 CRUD ====================

def get_categories(db: Session,
                   skip: int = 0, limit: int = 100, search: str | None = None):
    """获取库存分类列表（所有门店通用）"""
    query = db.query(InventoryCategory)
    if search:
        query = query.filter(InventoryCategory.name.like(f"%{search}%"))
    return query.offset(skip).limit(limit).all()


def get_category_by_id(db: Session, category_id: int):
    return db.query(InventoryCategory).filter(InventoryCategory.id == category_id).first()


def create_category(db: Session, category: InventoryCategoryCreate):
    db_cat = InventoryCategory(**category.model_dump())
    db.add(db_cat)
    db.commit()
    db.refresh(db_cat)
    return db_cat


def update_category(db: Session, category_id: int, category: InventoryCategoryUpdate):
    db_cat = get_category_by_id(db, category_id)
    if db_cat:
        update_data = category.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_cat, key, value)
        db.commit()
        db.refresh(db_cat)
    return db_cat


def soft_delete_category(db: Session, category_id: int) -> bool:
    db_cat = get_category_by_id(db, category_id)
    if not db_cat:
        return False
    db_cat.is_active = False
    db.commit()
    return True


# ==================== 物品 CRUD ====================

def get_items(db: Session, store_id: int | None = None, category_id: int | None = None,
              search: str | None = None, low_stock_only: bool = False,
              skip: int = 0, limit: int = 100):
    """获取物品列表，支持多条件过滤"""
    query = db.query(InventoryItem)
    if store_id is not None:
        query = query.filter(InventoryItem.store_id == store_id)
    if category_id is not None:
        query = query.filter(InventoryItem.category_id == category_id)
    if search:
        like = f"%{search}%"
        query = query.filter(
            (InventoryItem.name.like(like)) | (InventoryItem.sku.like(like))
        )
    if low_stock_only:
        query = query.filter(InventoryItem.quantity <= InventoryItem.safety_stock)
    return query.offset(skip).limit(limit).all()


def get_item_by_id(db: Session, item_id: int):
    return db.query(InventoryItem).filter(InventoryItem.id == item_id).first()


def get_item_by_sku(db: Session, sku: str):
    return db.query(InventoryItem).filter(InventoryItem.sku == sku).first()


def create_item(db: Session, item: InventoryItemCreate):
    existing = get_item_by_sku(db, item.sku)
    if existing:
        raise ValueError(f"SKU '{item.sku}' 已存在")
    db_item = InventoryItem(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_item(db: Session, item_id: int, item: InventoryItemUpdate):
    db_item = get_item_by_id(db, item_id)
    if db_item:
        update_data = item.model_dump(exclude_unset=True)
        if "sku" in update_data and update_data["sku"] != db_item.sku:
            conflict = db.query(InventoryItem).filter(
                InventoryItem.sku == update_data["sku"], InventoryItem.id != item_id
            ).first()
            if conflict:
                raise ValueError(f"SKU '{update_data['sku']}' 已被使用")
        for key, value in update_data.items():
            setattr(db_item, key, value)
        db.commit()
        db.refresh(db_item)
    return db_item


def soft_delete_item(db: Session, item_id: int) -> bool:
    db_item = get_item_by_id(db, item_id)
    if not db_item:
        return False
    db_item.is_active = False
    db.commit()
    return True


# ==================== 出入库操作 ====================

def stock_in(db: Session, item_id: int, quantity: float,
             operator_id: int, unit_price: float | None = None,
             remark: str | None = None):
    """入库：增加库存 + 记录流水。quantity 必须 > 0"""
    if quantity <= 0:
        raise ValueError("入库数量必须大于0")

    # 使用悲观行锁防止同时出入库导致的库存变动丢失
    db_item = db.query(InventoryItem).filter(
        InventoryItem.id == item_id
    ).with_for_update().first()
    if not db_item:
        raise ValueError("物品不存在")

    db_item.quantity += quantity
    if unit_price is not None:
        db_item.unit_price = unit_price

    log = InventoryLog(
        item_id=item_id,
        store_id=db_item.store_id,
        change_type="in",
        quantity_change=quantity,
        quantity_after=db_item.quantity,
        operator_id=operator_id,
        remark=remark,
    )
    db.add(log)
    db.commit()
    db.refresh(db_item)
    return db_item


def stock_out(db: Session, item_id: int, quantity: float,
              operator_id: int, remark: str | None = None):
    """出库：减少库存 + 记录流水。quantity 必须 > 0 且不超过现有库存"""
    if quantity <= 0:
        raise ValueError("出库数量必须大于0")

    # 使用悲观行锁防止并发出库超卖
    db_item = db.query(InventoryItem).filter(
        InventoryItem.id == item_id
    ).with_for_update().first()
    if not db_item:
        raise ValueError("物品不存在")
    if db_item.quantity < quantity:
        raise ValueError(f"库存不足，当前库存 {db_item.quantity}，需要 {quantity}")

    db_item.quantity -= quantity

    log = InventoryLog(
        item_id=item_id,
        store_id=db_item.store_id,
        change_type="out",
        quantity_change=-quantity,
        quantity_after=db_item.quantity,
        operator_id=operator_id,
        remark=remark,
    )
    db.add(log)
    db.commit()
    db.refresh(db_item)
    return db_item


# ==================== 流水查询 ====================

def get_logs(db: Session, store_id: int | None = None, item_id: int | None = None,
             change_type: str | None = None, operator_id: int | None = None,
             start_time: datetime | None = None, end_time: datetime | None = None,
             skip: int = 0, limit: int = 100):
    """查询库存流水，支持多条件过滤"""
    query = db.query(InventoryLog)
    if store_id is not None:
        query = query.filter(InventoryLog.store_id == store_id)
    if item_id is not None:
        query = query.filter(InventoryLog.item_id == item_id)
    if change_type:
        query = query.filter(InventoryLog.change_type == change_type)
    if operator_id is not None:
        query = query.filter(InventoryLog.operator_id == operator_id)
    if start_time:
        query = query.filter(InventoryLog.created_at >= start_time)
    if end_time:
        query = query.filter(InventoryLog.created_at <= end_time)
    return query.order_by(InventoryLog.created_at.desc()).offset(skip).limit(limit).all()
