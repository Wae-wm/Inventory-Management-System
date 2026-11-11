from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    full_name: str = Field(min_length=1, max_length=100)
    # bcrypt อ่านได้ไม่เกิน 72 byte จึงจำกัดความยาวไว้ที่ 72 ตัวอักษร
    password: str = Field(min_length=8, max_length=72)
    email: EmailStr | None = None
    role: Literal["ADMIN", "STAFF"] = "STAFF"


class UserOut(BaseModel):
    """ข้อมูลผู้ใช้ที่ส่งกลับให้ client ไม่มี password_hash โดยตั้งใจ"""

    model_config = ConfigDict(from_attributes=True)

    user_id: int
    username: str
    full_name: str
    email: str | None
    role: str
    is_active: bool
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
