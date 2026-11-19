from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers import (
    auth,
    categories,
    dashboard,
    products,
    stock,
    supplier_products,
    suppliers,
    users,
    warehouses,
)

app = FastAPI(title="Inventory Management System")
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(categories.router)
app.include_router(suppliers.router)
app.include_router(warehouses.router)
app.include_router(products.router)
app.include_router(supplier_products.router)
app.include_router(stock.router)
app.include_router(dashboard.router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/db")
def health_db(db: Session = Depends(get_db)):
    """ตรวจว่าเชื่อมต่อ MySQL ได้และเห็นกี่ตารางใน inventory_db"""
    tables = db.execute(text("SHOW TABLES")).fetchall()
    return {"database": "connected", "table_count": len(tables)}
