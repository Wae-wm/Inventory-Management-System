from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


def get_or_404(db: Session, model, obj_id: int, label: str):
    obj = db.get(model, obj_id)
    if obj is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"ไม่พบ{label}")
    return obj


def commit_or_409(db: Session, detail: str) -> None:
    """บันทึกข้อมูล ถ้าชนกับค่า unique ที่มีอยู่ให้ตอบ 409 แทนที่จะ error 500"""
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, detail=detail)


def apply_update(obj, data: BaseModel) -> None:
    """แก้เฉพาะฟิลด์ที่ client ส่งมา ฟิลด์ที่ฐานข้อมูลห้ามเป็นค่าว่างจะไม่ยอมรับ null"""
    columns = inspect(type(obj)).columns
    for key, value in data.model_dump(exclude_unset=True).items():
        if value is None and not columns[key].nullable:
            raise HTTPException(422, detail=f"{key} ห้ามเป็น null")
        setattr(obj, key, value)
