from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User
from app.security import hash_password


def create_user(
    db: Session,
    *,
    username: str,
    full_name: str,
    password: str,
    role: str = "STAFF",
    email: str | None = None,
) -> User:
    if db.scalar(select(User).where(User.username == username)):
        raise ValueError(f"มี username '{username}' อยู่แล้ว")
    user = User(
        username=username,
        full_name=full_name,
        password_hash=hash_password(password),
        role=role,
        email=email,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
