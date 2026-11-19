from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud import apply_update, commit_or_409, get_or_404
from app.database import get_db
from app.dependencies import get_current_user, require_admin
from app.models import Category
from app.schemas.category import CategoryCreate, CategoryOut, CategoryUpdate

# ทุก endpoint ต้องล็อกอิน ส่วนการเพิ่ม/แก้/ปิดใช้งานต้องเป็น Admin
router = APIRouter(prefix="/categories", tags=["categories"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=list[CategoryOut])
def list_categories(
    include_inactive: bool = False,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    stmt = select(Category).order_by(Category.category_id).offset(skip).limit(limit)
    if not include_inactive:
        stmt = stmt.where(Category.is_active.is_(True))
    return db.scalars(stmt).all()


@router.get("/{item_id}", response_model=CategoryOut)
def get_category(item_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, Category, item_id, "หมวดหมู่")


@router.post("", response_model=CategoryOut, status_code=201, dependencies=[Depends(require_admin)])
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    obj = Category(**data.model_dump())
    db.add(obj)
    commit_or_409(db, "ชื่อหมวดหมู่ซ้ำกับที่มีอยู่แล้ว")
    db.refresh(obj)
    return obj


@router.patch("/{item_id}", response_model=CategoryOut, dependencies=[Depends(require_admin)])
def update_category(item_id: int, data: CategoryUpdate, db: Session = Depends(get_db)):
    obj = get_or_404(db, Category, item_id, "หมวดหมู่")
    apply_update(obj, data)
    commit_or_409(db, "ชื่อหมวดหมู่ซ้ำกับที่มีอยู่แล้ว")
    db.refresh(obj)
    return obj


@router.delete("/{item_id}", status_code=204, dependencies=[Depends(require_admin)])
def deactivate_category(item_id: int, db: Session = Depends(get_db)):
    """ไม่ลบแถวจริง เพราะข้อมูลอื่นอ้างอิงอยู่ แค่ตั้ง is_active เป็น false"""
    obj = get_or_404(db, Category, item_id, "หมวดหมู่")
    obj.is_active = False
    db.commit()
