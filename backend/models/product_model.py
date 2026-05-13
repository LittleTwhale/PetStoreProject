# models/product_model.py — 商品管理模块
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database.database import Base


class Product(Base):
    """商品表（宠物用品 / 宠物活体售卖）"""
    __tablename__ = "products"
    __table_args__ = {'comment': '商品表(宠物用品/宠物活体售卖)'}

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, comment="所属门店")

    name = Column(String(100), nullable=False, comment="商品名称")
    product_type = Column(String(20), nullable=False, default="goods", comment="类型: goods(用品) / pet(活体)")
    pet_id = Column(Integer, ForeignKey("pets.id", ondelete="SET NULL"), nullable=True, comment="关联宠物(活体售卖时)")
    inventory_item_id = Column(Integer, ForeignKey("inventory_items.id", ondelete="SET NULL"), nullable=True, comment="关联库存(用品售卖时)")

    price = Column(Float, nullable=False, default=0, comment="售价")
    cost_price = Column(Float, nullable=True, comment="成本价")
    stock = Column(Integer, default=0, comment="库存量(用品类，活体类固定为1)")
    description = Column(Text, nullable=True, comment="商品描述")
    cover_image = Column(String(255), nullable=True, comment="封面图")

    is_active = Column(Boolean, default=True, comment="是否上架")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    pet = relationship("Pet", backref="products")
    inventory_item = relationship("InventoryItem", backref="products")
