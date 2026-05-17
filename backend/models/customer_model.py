# models/customer_model.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database.database import Base


class CustomerProfile(Base):
    __tablename__ = "customer_profiles"
    __table_args__ = {'comment': '客户业务档案表'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False,
                     comment="关联基础用户")

    real_name = Column(String(50), nullable=True, comment="客户真实姓名")
    phone = Column(String(20), nullable=True, index=True, comment="联系电话")
    address = Column(String(255), nullable=True, comment="联系地址(寄养接送需要)")

    # 业务数据
    membership_level = Column(String(20), default="普通会员", comment="会员等级")
    points = Column(Integer, default=0, comment="积分")
    balance = Column(Float, default=0.0, comment="账户余额")
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="SET NULL"), nullable=True, comment="所属门店")

    # 关联
    user = relationship("User", backref="customer_profile")
    pets = relationship("Pet", back_populates="owner")