# models/pet_model.py
from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, Float
from sqlalchemy.orm import relationship
from database.database import Base


class Pet(Base):
    __tablename__ = "pets"
    __table_args__ = {'comment': '宠物档案与资产表'}

    id = Column(Integer, primary_key=True, autoincrement=True)

    # owner_id 允许为空。如果客户被删除，宠物记录保留并将 owner_id 置空 (SET NULL)
    owner_id = Column(Integer, ForeignKey("customer_profiles.id", ondelete="SET NULL"), nullable=True,
                      comment="关联客户的主键(店内宠物为空)")

    # 业务状态与商业属性
    ownership_type = Column(String(20), nullable=False, default="customer",
                            comment="归属类型: customer(客宠) / for_sale(待售) / store_mascot(店宠)")
    price = Column(Float, nullable=True, comment="售价(仅待售宠物有效)")

    # 基础信息
    name = Column(String(50), nullable=True, comment="宠物昵称(待售宠物可能暂无名字)")
    species = Column(String(20), nullable=False, comment="物种(狗/猫/异宠)")
    breed = Column(String(50), nullable=True, comment="品种(如: 金毛/蓝猫)")
    gender = Column(String(10), nullable=True, comment="性别(公/母/未知)")
    weight = Column(Float, nullable=True, comment="体重(kg)")

    # 健康与生理状态
    birth_date = Column(Date, nullable=True, comment="出生日期")
    is_neutered = Column(Boolean, default=False, comment="是否绝育")
    vaccine_status = Column(String(255), nullable=True, comment="疫苗接种状态")

    avatar = Column(String(255), nullable=True, comment="宠物照片URL")
    special_notes = Column(String(500), nullable=True, comment="特殊注意事项")

    owner = relationship("CustomerProfile", back_populates="pets")