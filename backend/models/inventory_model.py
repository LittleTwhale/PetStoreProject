# models/inventory_model.py — 库存管理模块
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database.database import Base


class InventoryCategory(Base):
    """库存分类表"""
    __tablename__ = "inventory_categories"
    __table_args__ = {'comment': '库存分类表'}

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    name = Column(String(50), nullable=False, comment="分类名称(如:狗粮、猫砂、药品)")
    description = Column(String(200), nullable=True, comment="分类描述")
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, comment="所属门店")

    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    items = relationship("InventoryItem", back_populates="category", cascade="all, delete-orphan")


class InventoryItem(Base):
    """库存物品表"""
    __tablename__ = "inventory_items"
    __table_args__ = {'comment': '库存物品表'}

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    category_id = Column(Integer, ForeignKey("inventory_categories.id", ondelete="CASCADE"), nullable=False, comment="所属分类")
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, comment="所属门店")

    name = Column(String(100), nullable=False, comment="物品名称")
    sku = Column(String(50), unique=True, nullable=False, comment="SKU编码")
    unit = Column(String(20), default="个", comment="单位(袋/瓶/支/盒)")
    quantity = Column(Float, default=0, comment="当前库存数量")
    safety_stock = Column(Float, default=0, comment="安全库存阈值")
    unit_price = Column(Float, nullable=True, comment="进货单价")
    selling_price = Column(Float, nullable=True, comment="建议售价")
    supplier = Column(String(100), nullable=True, comment="供应商")

    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    category = relationship("InventoryCategory", back_populates="items")
    logs = relationship("InventoryLog", back_populates="item", cascade="all, delete-orphan")


class InventoryLog(Base):
    """库存流水日志表"""
    __tablename__ = "inventory_logs"
    __table_args__ = {'comment': '库存流水日志表'}

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    item_id = Column(Integer, ForeignKey("inventory_items.id", ondelete="CASCADE"), nullable=False, comment="物品ID")
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, comment="所属门店")
    change_type = Column(String(10), nullable=False, comment="变动类型: in(入库)/out(出库)/adjust(盘点调整)")
    quantity_change = Column(Float, nullable=False, comment="变动数量(正入负出)")
    quantity_after = Column(Float, nullable=False, comment="变动后数量")
    operator_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="操作人")
    remark = Column(String(255), nullable=True, comment="备注")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="操作时间")

    # 关系
    item = relationship("InventoryItem", back_populates="logs")
