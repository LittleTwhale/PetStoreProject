# models/service_model.py — 服务项目管理模块
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database.database import Base


class Service(Base):
    """服务项目表（美容/寄养/医疗/训练等）"""
    __tablename__ = "services"
    __table_args__ = {'comment': '服务项目表(美容/寄养/医疗/训练等)'}

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, comment="所属门店")

    name = Column(String(100), nullable=False, comment="服务名称(如:基础洗护)")
    category = Column(String(30), nullable=False, default="other", comment="服务分类: grooming(美容) / boarding(寄养) / medical(医疗) / training(训练) / other")
    price = Column(Float, nullable=False, default=0, comment="标准价格")
    duration_minutes = Column(Integer, default=0, comment="预计时长(分钟)")
    description = Column(Text, nullable=True, comment="服务说明")

    is_active = Column(Boolean, default=True, comment="是否上架")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
