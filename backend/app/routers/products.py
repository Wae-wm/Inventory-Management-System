from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.crud import apply_update, commit_or_409, get_or_404
from app.database import get_db
from app.dependencies import get_current_user, require_admin
from app.models import Category, Product
from app.schemas.product import ProductCreate, ProductOut, ProductUpdate

# ทุก endpoint ต้องล็อกอิน Staff เพิ่ม/แก้สินค้าได้ แต่ปิดใช้งานสินค้าได้เฉพาะ Admin
router = APIRouter(prefix="/products", tags=["products"], dependencies=[Depends(get_current_user)])


def _check_category(db: Session, category_id: int) -> None:
    category = db.get(Category, category_id)
    if category is None or not category.is_active:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="ไม่พบหมวดหมู่นี้ หรือหมวดหมู่ถูกปิดใช้งาน")


@router.get("", response_model=list[ProductOut])
def list_products(
    q: str | None = Query(None, description="ค้นหาจากชื่อสินค้าหรือ SKU"),
    category_id: int | None = None,
    include_inactive: bool = False,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    stmt = select(Product).order_by(Product.product_id).offset(skip).limit(limit)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(Product.product_name.like(like), Product.sku.like(like)))
    if category_id is not None:
        stmt = stmt.where(Product.category_id == category_id)
    if not include_inactive:
        stmt = stmt.where(Product.is_active.is_(True))
    return db.scalars(stmt).all()


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, Product, product_id, "สินค้า")


@router.post("", response_model=ProductOut, status_code=201)
def create_product(data: ProductCreate, db: Session = Depends(get_db)):
    _check_category(db, data.category_id)
    obj = Product(**data.model_dump())
    db.add(obj)
    commit_or_409(db, "SKU ซ้ำกับสินค้าที่มีอยู่แล้ว")
    db.refresh(obj)
    return obj


@router.patch("/{product_id}", response_model=ProductOut)
def update_product(product_id: int, data: ProductUpdate, db: Session = Depends(get_db)):
    obj = get_or_404(db, Product, product_id, "สินค้า")
    if data.category_id is not None and data.category_id != obj.category_id:
        _check_category(db, data.category_id)
    apply_update(obj, data)
    commit_or_409(db, "SKU ซ้ำกับสินค้าที่มีอยู่แล้ว")
    db.refresh(obj)
    return obj


@router.delete("/{product_id}", status_code=204, dependencies=[Depends(require_admin)])
def deactivate_product(product_id: int, db: Session = Depends(get_db)):
    """ไม่ลบแถวจริง เพราะประวัติรับเข้า-เบิกออกอ้างอิงสินค้านี้อยู่"""
    obj = get_or_404(db, Product, product_id, "สินค้า")
    obj.is_active = False
    db.commit()
