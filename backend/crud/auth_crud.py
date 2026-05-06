# crud/auth_crud.py
from sqlalchemy.orm import Session
from models.user_model import User, UserAuth


# ==================== 查询 ====================
def get_auth_by_identifier(db: Session, identifier: str) -> UserAuth | None:
    """根据账号(identifier)查询密码登录凭证"""
    return db.query(UserAuth).filter(
        UserAuth.identifier == identifier,
        UserAuth.identity_type == "password"
    ).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """根据用户ID查询用户基础信息"""
    return db.query(User).filter(User.id == user_id).first()


def check_identifier_exists(db: Session, identifier: str) -> bool:
    """检查账号是否已被注册"""
    return db.query(UserAuth).filter(
        UserAuth.identifier == identifier,
        UserAuth.identity_type == "password"
    ).first() is not None


def get_all_users(db: Session) -> list[User]:
    """获取所有用户列表"""
    return db.query(User).order_by(User.id.desc()).all()


# ==================== 创建 ====================
def create_user(
    db: Session,
    nickname: str = "神秘宠友",
    role: str = "customer",
    position_desc: str | None = None,
    avatar: str | None = None,
) -> User:
    """创建用户基础信息"""
    user = User(
        nickname=nickname,
        role=role,
        position_desc=position_desc,
        avatar=avatar,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_auth(
    db: Session,
    user_id: int,
    identifier: str,
    credential: str,
    identity_type: str = "password",
) -> UserAuth:
    """创建登录凭证"""
    auth = UserAuth(
        user_id=user_id,
        identity_type=identity_type,
        identifier=identifier,
        credential=credential,
    )
    db.add(auth)
    db.commit()
    db.refresh(auth)
    return auth


# ==================== 更新 ====================
def update_user(db: Session, user_id: int, **kwargs) -> User | None:
    """更新用户信息"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    for key, value in kwargs.items():
        if value is not None and hasattr(user, key):
            setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user
