# backend/schemas/customer_schema.py
from pydantic import BaseModel, ConfigDict
from typing import Optional, List

from schemas.pet_schema import PetResponse


class CustomerProfileBase(BaseModel):
    real_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    membership_level: Optional[str] = "普通会员"
    points: Optional[int] = 0
    balance: Optional[float] = 0.0


class CustomerProfileCreate(CustomerProfileBase):
    user_id: int  # 关联的基础用户ID


class CustomerProfileUpdate(CustomerProfileBase):
    pass


class CustomerProfileResponse(CustomerProfileBase):
    id: int
    user_id: int
    pets: List[PetResponse] = []  # 嵌套显示名下宠物

    model_config = ConfigDict(from_attributes=True)