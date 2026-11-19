from datetime import date, datetime, time, timedelta
from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_admin
from app.models import InventoryBalance, Product, StockMovement, User, Warehouse
from app.schemas.stock import (
    BalanceOut,
    LowStockOut,
    MovementOut,
    StockAdjust,
    StockIn,
    StockOut,
    StockResult,
)
from app.services.stock import record_movement

router = APIRouter(prefix="/stock", tags=["stock"], dependencies=[Depends(get_current_user)])


@router.post("/in", response_model=StockResult, status_code=201)
def stock_in(data: StockIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    movement, on_hand = record_movement(
        db, user_id=user.user_id, movement_type="IN", **data.model_dump()
    )
    return StockResult(movement=movement, quantity_on_hand=on_hand)


@router.post("/out", response_model=StockResult, status_code=201)
def stock_out(data: StockOut, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    movement, on_hand = record_movement(
        db, user_id=user.user_id, movement_type="OUT", **data.model_dump()
    )
    return StockResult(movement=movement, quantity_on_hand=on_hand)


@router.post("/adjust", response_model=StockResult, status_code=201)
def stock_adjust(data: StockAdjust, user: User = Depends(require_admin), db: Session = Depends(get_db)):
    """ปรับยอดตามที่นับได้จริง เฉพาะ Admin"""
    movement, on_hand = record_movement(
        db, user_id=user.user_id, movement_type="ADJUSTMENT", **data.model_dump()
    )
    return StockResult(movement=movement, quantity_on_hand=on_hand)


@router.get("/balances", response_model=list[BalanceOut])
def list_balances(
    product_id: int | None = None,
    warehouse_id: int | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    stmt = (
        select(InventoryBalance, Product, Warehouse)
        .join(Product, Product.product_id == InventoryBalance.product_id)
        .join(Warehouse, Warehouse.warehouse_id == InventoryBalance.warehouse_id)
        .order_by(InventoryBalance.product_id, InventoryBalance.warehouse_id)
        .offset(skip)
        .limit(limit)
    )
    if product_id is not None:
        stmt = stmt.where(InventoryBalance.product_id == product_id)
    if warehouse_id is not None:
        stmt = stmt.where(InventoryBalance.warehouse_id == warehouse_id)
    return [
        BalanceOut(
            inventory_id=b.inventory_id,
            product_id=p.product_id,
            sku=p.sku,
            product_name=p.product_name,
            warehouse_id=w.warehouse_id,
            warehouse_code=w.warehouse_code,
            quantity_on_hand=b.quantity_on_hand,
            updated_at=b.updated_at,
        )
        for b, p, w in db.execute(stmt).all()
    ]


@router.get("/movements", response_model=list[MovementOut])
def list_movements(
    product_id: int | None = None,
    warehouse_id: int | None = None,
    movement_type: Literal["IN", "OUT", "ADJUSTMENT"] | None = None,
    date_from: date | None = Query(None, description="วันที่เริ่ม (รวมวันนี้)"),
    date_to: date | None = Query(None, description="วันที่สิ้นสุด (รวมวันนี้)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """ประวัติการเคลื่อนไหว เรียงจากใหม่ไปเก่า"""
    stmt = (
        select(StockMovement)
        .order_by(StockMovement.created_at.desc(), StockMovement.movement_id.desc())
        .offset(skip)
        .limit(limit)
    )
    if product_id is not None:
        stmt = stmt.where(StockMovement.product_id == product_id)
    if warehouse_id is not None:
        stmt = stmt.where(StockMovement.warehouse_id == warehouse_id)
    if movement_type is not None:
        stmt = stmt.where(StockMovement.movement_type == movement_type)
    if date_from is not None:
        stmt = stmt.where(StockMovement.created_at >= datetime.combine(date_from, time.min))
    if date_to is not None:
        stmt = stmt.where(StockMovement.created_at < datetime.combine(date_to + timedelta(days=1), time.min))
    return db.scalars(stmt).all()


def low_stock_rows(db: Session):
    """สินค้าที่ยอดรวมทุกคลังน้อยกว่าหรือเท่ากับ reorder_level (สินค้าที่ยังไม่เคยรับเข้านับเป็น 0)"""
    total = func.coalesce(func.sum(InventoryBalance.quantity_on_hand), 0)
    stmt = (
        select(Product.product_id, Product.sku, Product.product_name, Product.reorder_level, total.label("total"))
        .outerjoin(InventoryBalance, InventoryBalance.product_id == Product.product_id)
        .where(Product.is_active.is_(True))
        .group_by(Product.product_id, Product.sku, Product.product_name, Product.reorder_level)
        .having(total <= Product.reorder_level)
        .order_by(Product.product_id)
    )
    return db.execute(stmt).all()


@router.get("/low-stock", response_model=list[LowStockOut])
def low_stock(db: Session = Depends(get_db)):
    return [
        LowStockOut(
            product_id=r.product_id,
            sku=r.sku,
            product_name=r.product_name,
            total_on_hand=int(r.total),
            reorder_level=r.reorder_level,
        )
        for r in low_stock_rows(db)
    ]
