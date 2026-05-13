# models/store_model.py — 多门店支持
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database.database import Base


class Store(Base):
    """门店信息表"""
    __tablename__ = "stores"
    __table_args__ = {'comment': '门店信息表'}

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    name = Column(String(100), nullable=False, comment="门店名称")
    code = Column(String(20), unique=True, nullable=False, comment="门店编码(如BJ001)")
    address = Column(String(255), nullable=True, comment="门店地址")
    phone = Column(String(20), nullable=True, comment="门店联系电话")
    manager_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="店长用户ID")

    is_active = Column(Boolean, default=True, comment="是否营业中")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    user_stores = relationship("UserStore", back_populates="store", cascade="all, delete-orphan")


class UserStore(Base):
    """用户-门店绑定表（多对多）"""
    __tablename__ = "user_stores"
    __table_args__ = {'comment': '用户-门店绑定表'}

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="用户ID")
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, comment="门店ID")
    is_primary = Column(Boolean, default=False, comment="是否主属门店")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="绑定时间")

    # 关系
    user = relationship("User", back_populates="user_stores")
    store = relationship("Store", back_populates="user_stores")
