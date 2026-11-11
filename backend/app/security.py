import bcrypt

# bcrypt อ่านรหัสผ่านได้สูงสุด 72 byte ส่วนที่เกินจะถูกตัดทิ้งเงียบ ๆ
MAX_PASSWORD_BYTES = 72


def hash_password(password: str) -> str:
    """แปลงรหัสผ่านเป็นข้อความที่ย้อนกลับไม่ได้ เพื่อเก็บใน users.password_hash"""
    data = password.encode("utf-8")
    if len(data) > MAX_PASSWORD_BYTES:
        raise ValueError("รหัสผ่านยาวเกิน 72 byte")
    return bcrypt.hashpw(data, bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """ตรวจว่ารหัสผ่านที่พิมพ์มาตรงกับค่าที่เก็บไว้หรือไม่"""
    data = password.encode("utf-8")
    if len(data) > MAX_PASSWORD_BYTES:
        return False
    return bcrypt.checkpw(data, password_hash.encode("utf-8"))


# ---------- JWT ----------
from datetime import datetime, timedelta, timezone

import jwt

from app.config import settings


def create_access_token(user_id: int) -> str:
    """ออก token ที่เก็บ user_id (ในฟิลด์ sub) และเวลาหมดอายุ"""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> int | None:
    """คืน user_id ถ้า token ถูกต้องและยังไม่หมดอายุ ไม่เช่นนั้นคืน None"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        return int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        return None
