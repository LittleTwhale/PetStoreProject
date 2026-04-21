# models/user_model.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database.database import Base

# 用户基础信息表
class User(Base):
    __tablename__ = "users"
    __table_args__ = {'comment': '用户基础信息表'}

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    nickname = Column(String(50), nullable=False, default="神秘宠友", comment="昵称")
    avatar = Column(String(255), nullable=True, comment="头像URL")

    # 角色和身份
    role = Column(String(20), nullable=False, default="customer", comment="系统角色: admin/staff/customer")
    position_desc = Column(String(100), nullable=True, comment="具体职位或身份描述(如: 高级宠物美容师/普通会员)")
    permissions = Column(JSON, nullable=True, comment="细粒度权限列表")

    # 状态与时间戳
    is_active = Column(Boolean, default=True, comment="是否激活(用于逻辑删除)")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 建立与授权表的关联 (一对多：一个用户可以有多种登录方式)
    auths = relationship("UserAuth", back_populates="user", cascade="all, delete-orphan")

# 用户登录授权表
class UserAuth(Base):
    __tablename__ = "user_auths"
    __table_args__ = {'comment': '用户登录授权表'}

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="关联的用户ID")

    # 核心授权字段
    identity_type = Column(String(20), nullable=False, comment="登录类型: password(网页端) / wechat(小程序)")
    identifier = Column(String(100), nullable=False, comment="标识符: 账号/手机号/邮箱 或 微信的OpenID")
    credential = Column(String(255), nullable=True, comment="密码凭证: 哈希加密后的密码 或 微信的Session_Key(可选)")

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 建立与用户表的关联
    user = relationship("User", back_populates="auths")