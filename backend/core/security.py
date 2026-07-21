# core/security.py
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import jwt
from jwt.exceptions import InvalidTokenError

from .config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from database.database import get_db
from models.user_model import User
from crud.auth_crud import get_user_by_id

# 配置 passlib 使用 bcrypt 算法
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Bearer Token 安全方案（用于 OpenAPI 文档）
security_scheme = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码是否正确(明文密码是否与哈希密码匹配)"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """对明文密码进行哈希加密（注册时用）"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """生成 JWT Token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    # 签发 Token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """解码并验证 JWT Token，返回 payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效或已过期的 Token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_admin(user: User) -> User:
    """检查当前用户是否为管理员，否则抛出403"""
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，仅管理员可执行此操作",
        )
    return user


def require_admin_or_staff(user: User) -> User:
    """检查当前用户是否为管理员或店员，否则抛出403"""
    if user.role not in ("admin", "staff"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，仅管理员和店员可执行此操作",
        )
    return user


# ==================== 门店权限辅助函数 ====================

def get_staff_store_ids(user: User, db) -> list[int] | None:
    """
    获取用户可见的门店ID列表。
    - admin 返回 None（表示全部门店可见）
    - staff 返回其绑定的门店ID列表
    """
    if user.role == "admin":
        return None
    # 延迟导入避免循环依赖
    from crud.store_crud import get_user_stores
    stores = get_user_stores(db, user.id)
    return [s.id for s in stores]


def get_effective_store_id(user: User, requested_store_id: int | None, db) -> int | None:
    """
    获取实际操作的门店ID。
    - admin 使用传入的 store_id（可为None）
    - staff 忽略传入参数，优先使用 is_primary 主属门店，无主属则取第一个绑定门店
    - 如果 staff 未绑定门店则抛出403
    """
    if user.role == "admin":
        return requested_store_id
    store_ids = get_staff_store_ids(user, db)
    if not store_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您尚未绑定任何门店，请联系管理员",
        )
    # 优先查找 is_primary 主属门店
    from models.store_model import UserStore
    primary = db.query(UserStore).filter(
        UserStore.user_id == user.id,
        UserStore.is_primary == True,
    ).first()
    if primary and primary.store_id in store_ids:
        return primary.store_id
    # 无主属门店则返回第一个绑定门店
    return store_ids[0]


def require_store_access(user: User, store_id: int, db):
    """
    检查用户是否有权访问指定门店。
    - admin 始终通过
    - staff 需验证是否绑定到该门店
    """
    if user.role == "admin":
        return
    store_ids = get_staff_store_ids(user, db)
    if not store_ids or store_id not in store_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问该门店的数据",
        )


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security_scheme)],
    db: Session = Depends(get_db),
) -> User:
    """从请求头的 Bearer Token 中解析当前用户（FastAPI 依赖注入用）"""
    payload = decode_access_token(credentials.credentials)
    user_id = int(payload.get("sub"))
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用",
        )
    return user
