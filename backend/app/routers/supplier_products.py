from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud import apply_update, commit_or_409
from app.database import get_db
from app.dependencies import get_current_user, require_admin
from app.models import Product, Supplier, SupplierProduct
from app.schemas.supplier_product import (
    SupplierProductCreate,
    SupplierProductOut,
    SupplierProductUpdate,
)

router = APIRouter(
    prefix="/supplier-products", tags=["supplier-products"], dependencies=[Depends(get_current_user)]
)


def _get_link(db: Session, supplier_id: int, product_id: int) -> SupplierProduct:
    link = db.get(SupplierProduct, (supplier_id, product_id))
    if link is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="ไม่พบความสัมพันธ์ระหว่างผู้จำหน่ายและสินค้านี้")
    return link


@router.get("", response_model=list[SupplierProductOut])
def list_links(
    supplier_id: int | None = None,
    product_id: int | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    stmt = select(SupplierProduct).order_by(SupplierProduct.supplier_id, SupplierProduct.product_id)
    if supplier_id is not None:
        stmt = stmt.where(SupplierProduct.supplier_id == supplier_id)
    if product_id is not None:
        stmt = stmt.where(SupplierProduct.product_id == product_id)
    return db.scalars(stmt.offset(skip).limit(limit)).all()


@router.post("", response_model=SupplierProductOut, status_code=201, dependencies=[Depends(require_admin)])
def create_link(data: SupplierProductCreate, db: Session = Depends(get_db)):
    if db.get(Supplier, data.supplier_id) is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="ไม่พบผู้จำหน่ายนี้")
    if db.get(Product, data.product_id) is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="ไม่พบสินค้านี้")
    link = SupplierProduct(**data.model_dump())
    db.add(link)
    commit_or_409(db, "ผู้จำหน่ายรายนี้เชื่อมกับสินค้านี้อยู่แล้ว")
    db.refresh(link)
    return link


@router.patch("/{supplier_id}/{product_id}", response_model=SupplierProductOut, dependencies=[Depends(require_admin)])
def update_link(supplier_id: int, product_id: int, data: SupplierProductUpdate, db: Session = Depends(get_db)):
    link = _get_link(db, supplier_id, product_id)
    apply_update(link, data)
    db.commit()
    db.refresh(link)
    return link


@router.delete("/{supplier_id}/{product_id}", status_code=204, dependencies=[Depends(require_admin)])
def delete_link(supplier_id: int, product_id: int, db: Session = Depends(get_db)):
    """ตารางนี้ไม่มีตารางอื่นอ้างอิง จึงลบแถวจริงได้"""
    db.delete(_get_link(db, supplier_id, product_id))
    db.commit()
