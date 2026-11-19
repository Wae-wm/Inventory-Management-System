from datetime import datetime, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import InventoryBalance, Product, StockMovement
from app.routers.stock import low_stock_rows

router = APIRouter(prefix="/dashboard", tags=["dashboard"], dependencies=[Depends(get_current_user)])


class DashboardSummary(BaseModel):
    active_products: int
    low_stock_count: int
    total_units: int
    total_stock_value: Decimal
    movements_last_7_days: int


@router.get("/summary", response_model=DashboardSummary)
def summary(db: Session = Depends(get_db)):
    active_products = db.scalar(select(func.count()).select_from(Product).where(Product.is_active.is_(True)))
    total_units, total_value = db.execute(
        select(
            func.coalesce(func.sum(InventoryBalance.quantity_on_hand), 0),
            func.coalesce(func.sum(InventoryBalance.quantity_on_hand * Product.cost_price), 0),
        ).join(Product, Product.product_id == InventoryBalance.product_id)
    ).one()
    since = datetime.now() - timedelta(days=7)
    movements = db.scalar(
        select(func.count()).select_from(StockMovement).where(StockMovement.created_at >= since)
    )
    return DashboardSummary(
        active_products=active_products,
        low_stock_count=len(low_stock_rows(db)),
        total_units=int(total_units),
        total_stock_value=Decimal(total_value).quantize(Decimal("0.01")),
        movements_last_7_days=movements,
    )
