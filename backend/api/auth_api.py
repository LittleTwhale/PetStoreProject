# api/auth_api.py
import os
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from database.database import get_db
from schemas.auth_schema import (
    LoginReq, TokenRes, UserInfo, RegisterReq, UserUpdateReq,
    AdminCreateUserReq, AdminUpdateUserReq, UserListItem, AvatarRes,
    ChangePasswordReq,
)
from crud import auth_crud
from core import security
from models.user_model import User

router = APIRouter(tags=["认证"])

# 头像存储目录
AVATAR_DIR = os.path.join(os.path.dirname(__file__), "..", "static", "avatars")
os.makedirs(AVATAR_DIR, exist_ok=True)

ALLOWED_AVATAR_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
MAX_AVATAR_SIZE = 5 * 1024 * 1024  # 5MB


def require_admin(current_user: User) -> User:
    """检查当前用户是否为管理员"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，仅管理员可执行此操作",
        )
    return current_user


# ==================== 登录 & 注册 ====================
@router.post("/login", response_model=TokenRes, summary="用户登录")
def login(login_data: LoginReq, db: Session = Depends(get_db)):
    auth_record = auth_crud.get_auth_by_identifier(db, identifier=login_data.identifier)

    if not auth_record or not security.verify_password(login_data.password, auth_record.credential):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账号或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = security.create_access_token(
        data={"sub": str(auth_record.user_id)}
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=TokenRes, summary="用户注册")
def register(reg_data: RegisterReq, db: Session = Depends(get_db)):
    # 检查账号是否已存在
    if auth_crud.check_identifier_exists(db, identifier=reg_data.identifier):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="该账号已被注册",
        )

    # 创建用户（默认角色为 customer）
    user = auth_crud.create_user(
        db,
        nickname=reg_data.nickname,
        role="customer",
    )

    # 创建登录凭证
    hashed_password = security.get_password_hash(reg_data.password)
    auth_crud.create_auth(
        db,
        user_id=user.id,
        identifier=reg_data.identifier,
        credential=hashed_password,
    )

    # 生成 Token，注册即登录
    access_token = security.create_access_token(
        data={"sub": str(user.id)}
    )

    return {"access_token": access_token, "token_type": "bearer"}


# ==================== 当前用户 ====================
@router.get("/me", response_model=UserInfo, summary="获取当前用户信息")
def get_me(
    current_user: Annotated[User, Depends(security.get_current_user)],
    db: Session = Depends(get_db),
):
    """需要携带有效的 Bearer Token，返回当前登录用户的基础信息（含登录账号）"""
    auth_record = auth_crud.get_auth_by_user_id(db, current_user.id)
    return {
        "id": current_user.id,
        "nickname": current_user.nickname,
        "avatar": current_user.avatar,
        "role": current_user.role,
        "position_desc": current_user.position_desc,
        "permissions": current_user.permissions,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at,
        "identifier": auth_record.identifier if auth_record else None,
    }


@router.put("/me", response_model=UserInfo, summary="更新当前用户信息")
def update_me(
    update_data: UserUpdateReq,
    current_user: Annotated[User, Depends(security.get_current_user)],
    db: Session = Depends(get_db),
):
    """更新当前登录用户的昵称和职位描述"""
    updated = auth_crud.update_user(
        db,
        user_id=current_user.id,
        nickname=update_data.nickname,
        position_desc=update_data.position_desc,
    )
    return updated


@router.post("/me/avatar", response_model=AvatarRes, summary="上传/更换头像")
def upload_avatar(
    current_user: Annotated[User, Depends(security.get_current_user)],
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
):
    """上传用户头像（支持 jpg/png/gif/webp，最大 5MB，自动清理旧头像文件）"""
    # 校验文件类型
    if file.content_type not in ALLOWED_AVATAR_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="仅支持 JPG、PNG、GIF、WebP 格式的图片",
        )

    # 校验文件大小
    contents = file.file.read()
    if len(contents) > MAX_AVATAR_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="头像文件大小不能超过 5MB",
        )

    # 清理旧头像文件
    if current_user.avatar and current_user.avatar.startswith("/static/avatars/"):
        old_filename = current_user.avatar.rsplit("/", 1)[-1]
        old_filepath = os.path.join(AVATAR_DIR, old_filename)
        if os.path.isfile(old_filepath):
            os.remove(old_filepath)

    # 生成唯一文件名
    ext = file.filename.rsplit(".", 1)[-1] if "." in (file.filename or "") else "png"
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(AVATAR_DIR, filename)

    # 写入文件
    with open(filepath, "wb") as f:
        f.write(contents)

    # 更新用户头像 URL
    avatar_url = f"/static/avatars/{filename}"
    auth_crud.update_user(db, user_id=current_user.id, avatar=avatar_url)

    return {"avatar_url": avatar_url}


@router.put("/me/password", summary="修改当前用户密码")
def change_password(
    pw_data: ChangePasswordReq,
    current_user: Annotated[User, Depends(security.get_current_user)],
    db: Session = Depends(get_db),
):
    """修改当前登录用户的密码，需提供旧密码验证"""
    auth_record = auth_crud.get_auth_by_user_id(db, current_user.id)
    if not auth_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前账号没有密码登录方式",
        )

    # 校验旧密码
    if not security.verify_password(pw_data.old_password, auth_record.credential):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码不正确",
        )

    # 哈希新密码并更新
    new_hashed = security.get_password_hash(pw_data.new_password)
    auth_crud.update_auth_credential(db, current_user.id, new_hashed)

    return {"detail": "密码已更新"}


# ==================== 管理员接口 ====================
@router.get("/admin/users", response_model=list[UserListItem], summary="管理员-获取用户列表")
def admin_list_users(
        current_user: Annotated[User, Depends(security.get_current_user)],
        db: Session = Depends(get_db),
):
    """管理员获取所有用户列表"""
    require_admin(current_user)
    users = auth_crud.get_all_users(db)  # list[User]

    result = []
    for user in users:
        # 获取该用户的 password 登录凭证中的 identifier
        identifier = next(
            (auth.identifier for auth in user.auths if auth.identity_type == "password"),
            None
        )
        # 构造符合 UserListItem 的字典
        result.append({
            "id": user.id,
            "identifier": identifier,
            "nickname": user.nickname,
            "avatar": user.avatar,
            "role": user.role,
            "position_desc": user.position_desc,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        })
    return result


@router.post("/admin/users", response_model=UserInfo, summary="管理员-创建用户")
def admin_create_user(
    user_data: AdminCreateUserReq,
    current_user: Annotated[User, Depends(security.get_current_user)],
    db: Session = Depends(get_db),
):
    """管理员创建新用户"""
    require_admin(current_user)

    if auth_crud.check_identifier_exists(db, identifier=user_data.identifier):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="该账号已被注册",
        )

    user = auth_crud.create_user(
        db,
        nickname=user_data.nickname,
        role=user_data.role,
        position_desc=user_data.position_desc,
    )

    hashed_password = security.get_password_hash(user_data.password)
    auth_crud.create_auth(
        db,
        user_id=user.id,
        identifier=user_data.identifier,
        credential=hashed_password,
    )

    return user


@router.put("/admin/users/{user_id}", response_model=UserInfo, summary="管理员-更新用户")
def admin_update_user(
    user_id: int,
    user_data: AdminUpdateUserReq,
    current_user: Annotated[User, Depends(security.get_current_user)],
    db: Session = Depends(get_db),
):
    """管理员更新用户信息（角色、状态、权限等）"""
    require_admin(current_user)

    # 构建更新字段
    update_kwargs = {}
    if user_data.nickname is not None:
        update_kwargs["nickname"] = user_data.nickname
    if user_data.role is not None:
        update_kwargs["role"] = user_data.role
    if user_data.position_desc is not None:
        update_kwargs["position_desc"] = user_data.position_desc
    if user_data.is_active is not None:
        update_kwargs["is_active"] = user_data.is_active
    if user_data.permissions is not None:
        update_kwargs["permissions"] = user_data.permissions

    updated = auth_crud.update_user(db, user_id=user_id, **update_kwargs)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
    return updated


@router.delete("/admin/users/{user_id}", summary="管理员-删除用户")
def admin_delete_user(
    user_id: int,
    current_user: Annotated[User, Depends(security.get_current_user)],
    db: Session = Depends(get_db),
):
    """管理员删除用户（级联删除关联的登录凭证）"""
    require_admin(current_user)

    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己",
        )

    # 清理被删除用户的头像文件
    target_user = auth_crud.get_user_by_id(db, user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
    if target_user.avatar and target_user.avatar.startswith("/static/avatars/"):
        old_filename = target_user.avatar.rsplit("/", 1)[-1]
        old_filepath = os.path.join(AVATAR_DIR, old_filename)
        if os.path.isfile(old_filepath):
            os.remove(old_filepath)

    auth_crud.delete_user(db, user_id)
    return {"detail": "用户已删除"}
