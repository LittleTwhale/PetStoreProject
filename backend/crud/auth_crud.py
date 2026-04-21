# crud/auth_crud.py
from sqlalchemy.orm import Session
from models.user_model import UserAuth

def get_auth_by_identifier(db: Session, identifier: str) -> UserAuth | None:
    """
    根据账号(identifier)查询密码登录凭证
    """
    return db.query(UserAuth).filter(
        UserAuth.identifier == identifier,
        UserAuth.identity_type == "password" # 严格限制为密码登录类型
    ).first()