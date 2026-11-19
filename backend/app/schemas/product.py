from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

Price = Decimal  # ราคา: ไม่ติดลบ ทศนิยมไม่เกิน 2 ตำแหน่ง


class ProductCreate(BaseModel):
    sku: str = Field(min_length=1, max_length=50)
    product_name: str = Field(min_length=1, max_length=150)
    category_id: int
    description: str | None = None
    unit: str = Field(default="piece", min_length=1, max_length=30)
    cost_price: Price = Field(default=Decimal("0"), ge=0, max_digits=10, decimal_places=2)
    selling_price: Price = Field(default=Decimal("0"), ge=0, max_digits=10, decimal_places=2)
    reorder_level: int = Field(default=10, ge=0)


class ProductUpdate(BaseModel):
    sku: str | None = Field(default=None, min_length=1, max_length=50)
    product_name: str | None = Field(default=None, min_length=1, max_length=150)
    category_id: int | None = None
    description: str | None = None
    unit: str | None = Field(default=None, min_length=1, max_length=30)
    cost_price: Price | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    selling_price: Price | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    reorder_level: int | None = Field(default=None, ge=0)
    is_active: bool | None = None


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: int
    sku: str
    product_name: str
    category_id: int
    description: str | None
    unit: str
    cost_price: Decimal
    selling_price: Decimal
    reorder_level: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
