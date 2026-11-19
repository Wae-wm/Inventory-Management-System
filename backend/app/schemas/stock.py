from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class StockIn(BaseModel):
    product_id: int
    warehouse_id: int
    quantity: int = Field(gt=0, le=1_000_000)
    reference_no: str | None = Field(default=None, max_length=50)
    note: str | None = None


class StockOut(StockIn):
    """เบิกออก ใช้ฟิลด์เดียวกับรับเข้า"""


class StockAdjust(BaseModel):
    """ปรับยอดตามที่นับได้จริง ระบบคำนวณส่วนต่างให้เอง"""

    product_id: int
    warehouse_id: int
    counted_quantity: int = Field(ge=0, le=1_000_000)
    note: str = Field(min_length=1, description="เหตุผลของการปรับยอด จำเป็นต้องระบุ")
    reference_no: str | None = Field(default=None, max_length=50)


class MovementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    movement_id: int
    product_id: int
    warehouse_id: int
    user_id: int
    movement_type: Literal["IN", "OUT", "ADJUSTMENT"]
    quantity: int
    reference_no: str | None
    note: str | None
    created_at: datetime


class StockResult(BaseModel):
    movement: MovementOut
    quantity_on_hand: int


class BalanceOut(BaseModel):
    inventory_id: int
    product_id: int
    sku: str
    product_name: str
    warehouse_id: int
    warehouse_code: str
    quantity_on_hand: int
    updated_at: datetime


class LowStockOut(BaseModel):
    product_id: int
    sku: str
    product_name: str
    total_on_hand: int
    reorder_level: int
