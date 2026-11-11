from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_admin
from app.schemas.user import UserCreate, UserOut
from app.services.users import create_user

router = APIRouter(prefix="/users", tags=["users"], dependencies=[Depends(require_admin)])


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create(data: UserCreate, db: Session = Depends(get_db)):
    """สร้างผู้ใช้ใหม่ เรียกได้เฉพาะ Admin"""
    try:
        return create_user(db, **data.model_dump())
    except ValueError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(e))
    except IntegrityError:  # เช่น email ซ้ำ
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, detail="ข้อมูลซ้ำกับผู้ใช้ที่มีอยู่แล้ว")
