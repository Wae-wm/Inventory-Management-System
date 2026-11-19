from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class SupplierProductCreate(BaseModel):
    supplier_id: int
    product_id: int
    supplier_sku: str | None = Field(default=None, max_length=50)
    unit_cost: Decimal = Field(default=Decimal("0"), ge=0, max_digits=10, decimal_places=2)
    lead_time_days: int = Field(default=0, ge=0)
    is_preferred: bool = False


class SupplierProductUpdate(BaseModel):
    supplier_sku: str | None = Field(default=None, max_length=50)
    unit_cost: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    lead_time_days: int | None = Field(default=None, ge=0)
    is_preferred: bool | None = None


class SupplierProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    supplier_id: int
    product_id: int
    supplier_sku: str | None
    unit_cost: Decimal
    lead_time_days: int
    is_preferred: bool
    created_at: datetime
