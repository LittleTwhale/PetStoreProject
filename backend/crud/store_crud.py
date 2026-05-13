# crud/store_crud.py — 门店管理与用户绑定
from sqlalchemy.orm import Session
from models.store_model import Store, UserStore
from models.user_model import User
from schemas.store_schema import StoreCreate, StoreUpdate, UserStoreCreate


# ==================== 门店 CRUD ====================

def get_stores(db: Session, skip: int = 0, limit: int = 100, search: str | None = None,
               is_active_only: bool = False):
    """获取门店列表，支持搜索和状态过滤"""
    query = db.query(Store)
    if search:
        like = f"%{search}%"
        query = query.filter(
            (Store.name.like(like)) | (Store.code.like(like))
        )
    if is_active_only:
        query = query.filter(Store.is_active == True)
    return query.offset(skip).limit(limit).all()


def get_store_by_id(db: Session, store_id: int):
    return db.query(Store).filter(Store.id == store_id).first()


def get_store_by_code(db: Session, code: str):
    return db.query(Store).filter(Store.code == code).first()


def create_store(db: Session, store: StoreCreate):
    """创建门店，编码唯一性校验"""
    existing = db.query(Store).filter(Store.code == store.code).first()
    if existing:
        raise ValueError(f"门店编码 '{store.code}' 已存在")
    db_store = Store(**store.model_dump())
    db.add(db_store)
    db.commit()
    db.refresh(db_store)
    return db_store


def update_store(db: Session, store_id: int, store: StoreUpdate):
    db_store = get_store_by_id(db, store_id)
    if db_store:
        update_data = store.model_dump(exclude_unset=True)
        # 如果修改了编码，检查是否与其他门店冲突
        if "code" in update_data and update_data["code"] != db_store.code:
            conflict = db.query(Store).filter(
                Store.code == update_data["code"], Store.id != store_id
            ).first()
            if conflict:
                raise ValueError(f"门店编码 '{update_data['code']}' 已被使用")
        for key, value in update_data.items():
            setattr(db_store, key, value)
        db.commit()
        db.refresh(db_store)
    return db_store


def soft_delete_store(db: Session, store_id: int) -> bool:
    """停用门店（逻辑删除）"""
    db_store = get_store_by_id(db, store_id)
    if not db_store:
        return False
    db_store.is_active = False
    db.commit()
    return True


# ==================== 用户-门店绑定 ====================

def get_user_stores(db: Session, user_id: int):
    """获取某用户绑定的所有门店"""
    return db.query(Store).join(UserStore, UserStore.store_id == Store.id).filter(
        UserStore.user_id == user_id
    ).all()


def get_store_users(db: Session, store_id: int):
    """获取某门店下绑定的所有用户（含用户详情）"""
    return db.query(UserStore, User).join(User, User.id == UserStore.user_id).filter(
        UserStore.store_id == store_id
    ).all()


def bind_user_to_store(db: Session, data: UserStoreCreate):
    """将用户绑定到门店，重复绑定抛出异常"""
    existing = db.query(UserStore).filter(
        UserStore.user_id == data.user_id,
        UserStore.store_id == data.store_id,
    ).first()
    if existing:
        raise ValueError("该用户已绑定到此门店")
    # 验证用户存在
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise ValueError("用户不存在")
    # 验证门店存在
    store = get_store_by_id(db, data.store_id)
    if not store:
        raise ValueError("门店不存在")

    db_us = UserStore(**data.model_dump())
    db.add(db_us)
    db.commit()
    db.refresh(db_us)
    return db_us


def unbind_user_from_store(db: Session, user_id: int, store_id: int) -> bool:
    """解除用户与门店的绑定"""
    record = db.query(UserStore).filter(
        UserStore.user_id == user_id,
        UserStore.store_id == store_id,
    ).first()
    if not record:
        return False
    db.delete(record)
    db.commit()
    return True
