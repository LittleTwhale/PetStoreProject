# api/auth_api.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.database import get_db  # 假设你有这个获取数据库 session 的依赖
from schemas.auth_schema import LoginReq, TokenRes
from crud import auth_crud
from core import security

router = APIRouter()


@router.post("/login", response_model=TokenRes, summary="用户登录")
def login(login_data: LoginReq, db: Session = Depends(get_db)):
    # 1. 查询数据库中是否有该账号
    auth_record = auth_crud.get_auth_by_identifier(db, identifier=login_data.identifier)

    # 2. 账号不存在或密码验证失败，统一返回 401 (防爆破)
    if not auth_record or not security.verify_password(login_data.password, auth_record.credential):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账号或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. 验证通过，生成 Token (将 user_id 作为载荷存入 Token)
    access_token = security.create_access_token(
        data={"sub": str(auth_record.user_id)}  # sub 是 JWT 标准的 subject
    )

    # 4. 返回 Token 给前端
    return {"access_token": access_token, "token_type": "bearer"}