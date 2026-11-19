from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class WarehouseCreate(BaseModel):
    warehouse_code: str = Field(min_length=1, max_length=20)
    warehouse_name: str = Field(min_length=1, max_length=150)
    address: str | None = None
    contact_name: str | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, max_length=20)


class WarehouseUpdate(BaseModel):
    warehouse_code: str | None = Field(default=None, min_length=1, max_length=20)
    warehouse_name: str | None = Field(default=None, min_length=1, max_length=150)
    address: str | None = None
    contact_name: str | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, max_length=20)
    is_active: bool | None = None


class WarehouseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    warehouse_id: int
    warehouse_code: str
    warehouse_name: str
    address: str | None
    contact_name: str | None
    phone: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
