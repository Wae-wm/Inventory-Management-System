from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud import apply_update, commit_or_409, get_or_404
from app.database import get_db
from app.dependencies import get_current_user, require_admin
from app.models import Supplier
from app.schemas.supplier import SupplierCreate, SupplierOut, SupplierUpdate

# ทุก endpoint ต้องล็อกอิน ส่วนการเพิ่ม/แก้/ปิดใช้งานต้องเป็น Admin
router = APIRouter(prefix="/suppliers", tags=["suppliers"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=list[SupplierOut])
def list_suppliers(
    include_inactive: bool = False,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    stmt = select(Supplier).order_by(Supplier.supplier_id).offset(skip).limit(limit)
    if not include_inactive:
        stmt = stmt.where(Supplier.is_active.is_(True))
    return db.scalars(stmt).all()


@router.get("/{item_id}", response_model=SupplierOut)
def get_supplier(item_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, Supplier, item_id, "ผู้จำหน่าย")


@router.post("", response_model=SupplierOut, status_code=201, dependencies=[Depends(require_admin)])
def create_supplier(data: SupplierCreate, db: Session = Depends(get_db)):
    obj = Supplier(**data.model_dump())
    db.add(obj)
    commit_or_409(db, "ข้อมูลซ้ำกับที่มีอยู่แล้ว")
    db.refresh(obj)
    return obj


@router.patch("/{item_id}", response_model=SupplierOut, dependencies=[Depends(require_admin)])
def update_supplier(item_id: int, data: SupplierUpdate, db: Session = Depends(get_db)):
    obj = get_or_404(db, Supplier, item_id, "ผู้จำหน่าย")
    apply_update(obj, data)
    commit_or_409(db, "ข้อมูลซ้ำกับที่มีอยู่แล้ว")
    db.refresh(obj)
    return obj


@router.delete("/{item_id}", status_code=204, dependencies=[Depends(require_admin)])
def deactivate_supplier(item_id: int, db: Session = Depends(get_db)):
    """ไม่ลบแถวจริง เพราะข้อมูลอื่นอ้างอิงอยู่ แค่ตั้ง is_active เป็น false"""
    obj = get_or_404(db, Supplier, item_id, "ผู้จำหน่าย")
    obj.is_active = False
    db.commit()
