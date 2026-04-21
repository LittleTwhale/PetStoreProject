# core/security.py
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
import jwt

from .config import SECRET_KEY,ALGORITHM,ACCESS_TOKEN_EXPIRE_MINUTES

# 配置 passlib 使用 bcrypt 算法
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    # 签发 Token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt