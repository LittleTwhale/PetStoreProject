# models/order_model.py — 订单管理模块
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database.database import Base


class Order(Base):
    """订单表（销售订单 / 服务订单）"""
    __tablename__ = "orders"
    __table_args__ = {'comment': '订单表(销售订单/服务订单)'}

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    order_no = Column(String(30), unique=True, nullable=False, comment="订单编号")
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, comment="所属门店")

    order_type = Column(String(20), nullable=False, comment="类型: sale(销售) / service(服务)")
    customer_id = Column(Integer, ForeignKey("customer_profiles.id", ondelete="SET NULL"), nullable=True, comment="客户ID(可为空，散客)")

    total_amount = Column(Float, nullable=False, default=0, comment="订单总金额")
    discount_amount = Column(Float, default=0, comment="优惠金额")
    final_amount = Column(Float, nullable=False, default=0, comment="实付金额")
    payment_method = Column(String(20), nullable=False, default="cash", comment="支付方式: cash/wechat/alipay/card/balance")

    status = Column(String(20), nullable=False, default="pending", comment="状态: pending/paid/completed/cancelled/refunded")
    operator_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="经手店员")
    remark = Column(String(255), nullable=True, comment="备注")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    customer = relationship("CustomerProfile", backref="orders")
    operator = relationship("User", backref="orders", foreign_keys=[operator_id])


class OrderItem(Base):
    """订单明细表"""
    __tablename__ = "order_items"
    __table_args__ = {'comment': '订单明细表'}

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, comment="订单ID")

    item_type = Column(String(20), nullable=False, comment="明细类型: product / service")
    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True, comment="商品ID")
    service_id = Column(Integer, ForeignKey("services.id", ondelete="SET NULL"), nullable=True, comment="服务ID")

    quantity = Column(Integer, default=1, comment="数量")
    unit_price = Column(Float, nullable=False, comment="单价")
    subtotal = Column(Float, nullable=False, comment="小计")
    staff_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="负责店员(服务类)")

    # 关系
    order = relationship("Order", back_populates="items")
    product = relationship("Product", backref="order_items")
    service = relationship("Service", backref="order_items")
    staff = relationship("User", backref="assigned_order_items", foreign_keys=[staff_id])
