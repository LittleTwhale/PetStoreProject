# upload_utils.py — 文件上传工具（独立模块，避免循环导入）
import os
import uuid
from typing import Optional

from fastapi import HTTPException, UploadFile

# 项目根目录（backend/ 的上一级）
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 上传文件根目录
UPLOADS_DIR = os.path.join(PROJECT_ROOT, "uploads")
for sub in ["avatars", "products", "pets"]:
    os.makedirs(os.path.join(UPLOADS_DIR, sub), exist_ok=True)

# 允许的图片类型和大小限制
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB


def save_upload_image(file: UploadFile, subdir: str) -> str:
    """保存上传的图片文件到指定子目录，返回相对 URL 路径"""
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="仅支持 JPG/PNG/GIF/WebP 格式")
    contents = file.file.read()
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="上传文件为空")
    if len(contents) > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=400, detail="文件大小不能超过 5MB")
    ext = (file.filename or "image.png").rsplit(".", 1)[-1].lower()
    if ext not in ("jpg", "jpeg", "png", "gif", "webp"):
        ext = "png"
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(UPLOADS_DIR, subdir, filename)
    with open(filepath, "wb") as f:
        f.write(contents)
    return f"/uploads/{subdir}/{filename}"


def remove_upload_image(url_path: Optional[str]) -> None:
    """根据 URL 路径删除上传文件"""
    if not url_path or not url_path.startswith("/uploads/"):
        return
    filepath = os.path.join(PROJECT_ROOT, url_path.lstrip("/"))
    if os.path.isfile(filepath):
        os.remove(filepath)
