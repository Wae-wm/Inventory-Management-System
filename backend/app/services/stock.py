from typing import Literal

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import InventoryBalance, Product, StockMovement, Warehouse

MovementType = Literal["IN", "OUT", "ADJUSTMENT"]


def _active_or_error(db: Session, model, obj_id: int, label: str):
    obj = db.get(model, obj_id)
    if obj is None:
        raise HTTPException(404, detail=f"ไม่พบ{label}")
    if not obj.is_active:
        raise HTTPException(400, detail=f"{label}นี้ถูกปิดใช้งาน")
    return obj


def _lock_balance(db: Session, product_id: int, warehouse_id: int, create: bool):
    """ดึงแถวยอดคงเหลือพร้อมล็อก (SELECT ... FOR UPDATE)
    ระหว่างที่ transaction นี้ยังไม่จบ คำขออื่นที่แตะแถวเดียวกันต้องรอ จึงไม่เกิดการเบิกซ้อนจนยอดติดลบ"""
    stmt = (
        select(InventoryBalance)
        .where(
            InventoryBalance.product_id == product_id,
            InventoryBalance.warehouse_id == warehouse_id,
        )
        .with_for_update()
    )
    balance = db.scalar(stmt)
    if balance is None and create:
        balance = InventoryBalance(product_id=product_id, warehouse_id=warehouse_id, quantity_on_hand=0)
        db.add(balance)
        try:
            db.flush()
        except IntegrityError:  # มีคำขออื่นสร้างแถวนี้พร้อมกัน
            db.rollback()
            raise HTTPException(409, detail="มีรายการอื่นกำลังสร้างยอดของสินค้านี้ในคลังเดียวกัน กรุณาลองอีกครั้ง")
    return balance


def record_movement(
    db: Session,
    *,
    user_id: int,
    product_id: int,
    warehouse_id: int,
    movement_type: MovementType,
    quantity: int | None = None,
    counted_quantity: int | None = None,
    reference_no: str | None = None,
    note: str | None = None,
) -> tuple[StockMovement, int]:
    """บันทึกประวัติ (stock_movements) และแก้ยอดคงเหลือ (inventory_balances) ใน transaction เดียว
    ถ้าขั้นไหนล้มเหลว ทั้งสองตารางจะไม่เปลี่ยนเลย"""
    _active_or_error(db, Product, product_id, "สินค้า")
    _active_or_error(db, Warehouse, warehouse_id, "คลังสินค้า")

    balance = _lock_balance(db, product_id, warehouse_id, create=movement_type != "OUT")
    on_hand = balance.quantity_on_hand if balance else 0

    if movement_type == "IN":
        delta, stored_qty = quantity, quantity
    elif movement_type == "OUT":
        if quantity > on_hand:
            raise HTTPException(409, detail=f"สินค้าไม่พอ คงเหลือ {on_hand} แต่ต้องการเบิก {quantity}")
        delta, stored_qty = -quantity, quantity
    else:  # ADJUSTMENT
        delta = counted_quantity - on_hand
        if delta == 0:
            raise HTTPException(400, detail="ยอดที่นับได้ตรงกับยอดในระบบอยู่แล้ว ไม่ต้องปรับ")
        stored_qty = delta  # เก็บแบบมีเครื่องหมาย เพื่อบอกว่าเพิ่มหรือลด

    new_on_hand = on_hand + delta
    balance.quantity_on_hand = new_on_hand
    movement = StockMovement(
        product_id=product_id,
        warehouse_id=warehouse_id,
        user_id=user_id,
        movement_type=movement_type,
        quantity=stored_qty,
        reference_no=reference_no,
        note=note,
    )
    db.add(movement)
    db.commit()
    db.refresh(movement)
    return movement, new_on_hand
