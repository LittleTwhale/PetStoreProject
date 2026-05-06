# crud/auth_crud.py
from sqlalchemy.orm import Session
from models.user_model import User, UserAuth


def get_auth_by_identifier(db: Session, identifier: str) -> UserAuth | None:
    """
    根据账号(identifier)查询密码登录凭证
    """
    return db.query(UserAuth).filter(
        UserAuth.identifier == identifier,
        UserAuth.identity_type == "password"  # 严格限制为密码登录类型
    ).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """
    根据用户ID查询用户基础信息
    """
    return db.query(User).filter(User.id == user_id).first()