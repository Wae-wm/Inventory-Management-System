from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db

app = FastAPI(title="Inventory Management System")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/db")
def health_db(db: Session = Depends(get_db)):
    """ตรวจว่าเชื่อมต่อ MySQL ได้และเห็นกี่ตารางใน inventory_db"""
    tables = db.execute(text("SHOW TABLES")).fetchall()
    return {"database": "connected", "table_count": len(tables)}
