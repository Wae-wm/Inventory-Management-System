from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud import apply_update, commit_or_409, get_or_404
from app.database import get_db
from app.dependencies import get_current_user, require_admin
from app.models import Warehouse
from app.schemas.warehouse import WarehouseCreate, WarehouseOut, WarehouseUpdate

# ทุก endpoint ต้องล็อกอิน ส่วนการเพิ่ม/แก้/ปิดใช้งานต้องเป็น Admin
router = APIRouter(prefix="/warehouses", tags=["warehouses"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=list[WarehouseOut])
def list_warehouses(
    include_inactive: bool = False,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    stmt = select(Warehouse).order_by(Warehouse.warehouse_id).offset(skip).limit(limit)
    if not include_inactive:
        stmt = stmt.where(Warehouse.is_active.is_(True))
    return db.scalars(stmt).all()


@router.get("/{item_id}", response_model=WarehouseOut)
def get_warehouse(item_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, Warehouse, item_id, "คลังสินค้า")


@router.post("", response_model=WarehouseOut, status_code=201, dependencies=[Depends(require_admin)])
def create_warehouse(data: WarehouseCreate, db: Session = Depends(get_db)):
    obj = Warehouse(**data.model_dump())
    db.add(obj)
    commit_or_409(db, "รหัสคลังซ้ำกับที่มีอยู่แล้ว")
    db.refresh(obj)
    return obj


@router.patch("/{item_id}", response_model=WarehouseOut, dependencies=[Depends(require_admin)])
def update_warehouse(item_id: int, data: WarehouseUpdate, db: Session = Depends(get_db)):
    obj = get_or_404(db, Warehouse, item_id, "คลังสินค้า")
    apply_update(obj, data)
    commit_or_409(db, "รหัสคลังซ้ำกับที่มีอยู่แล้ว")
    db.refresh(obj)
    return obj


@router.delete("/{item_id}", status_code=204, dependencies=[Depends(require_admin)])
def deactivate_warehouse(item_id: int, db: Session = Depends(get_db)):
    """ไม่ลบแถวจริง เพราะข้อมูลอื่นอ้างอิงอยู่ แค่ตั้ง is_active เป็น false"""
    obj = get_or_404(db, Warehouse, item_id, "คลังสินค้า")
    obj.is_active = False
    db.commit()
